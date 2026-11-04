"""Testes de calendário, unidades, cobertura e ausência das novas derivadas."""
import unittest

import numpy as np
import pandas as pd

from harmonizacao_economia import (
    anualizar_chuva, anualizar_precos, criar_interacoes,
    preparar_gaez, produtividade_historica,
)


def precos_teste(anos=(1999, 2000, 2001, 2002, 2024)):
    linhas = []
    for ano in anos:
        for mes in range(1, 13):
            linhas.append({"data": f"{ano}-{mes:02d}-01", "variavel": "price_soja",
                           "preco_nominal": 100.0 + mes, "moeda": "USD"})
    return pd.DataFrame(linhas)


def indice_teste():
    data = pd.date_range("1999-01-01", "2024-12-01", freq="MS")
    return pd.DataFrame({"data": data, "indice_precos": np.where(data.year == 2024, 24.0, data.month)})


class PrecosTest(unittest.TestCase):
    def test_deflacao_mensal_antes_da_media_e_log_da_media(self):
        out = anualizar_precos(precos_teste(), indice_teste()).set_index("ano")
        esperado = np.mean([(100 + m) * 24 / m for m in range(1, 13)])
        self.assertAlmostEqual(out.loc[2000, "preco_real_usd2024_media_anual"], esperado)
        self.assertNotAlmostEqual(esperado, 106.5 * 24 / 6.5)
        self.assertAlmostEqual(out.loc[2000, "ln_preco_nominal_media_anual"], np.log(106.5))
        self.assertAlmostEqual(out.loc[2001, "preco_real_usd2024_media_anual_lag1"], esperado)
        self.assertIn(2000, out.index)

    def test_lag_nao_pula_ano_ausente(self):
        out = anualizar_precos(precos_teste((2000, 2002, 2024))).set_index("ano")
        self.assertTrue(pd.isna(out.loc[2002, "preco_nominal_media_anual_lag1"]))

    def test_mes_faltante_nao_e_preco_anual(self):
        base = precos_teste()
        base = base.loc[base.data.ne("2000-12-01")]
        out = anualizar_precos(base, indice_teste()).set_index("ano")
        self.assertTrue(pd.isna(out.loc[2000, "preco_nominal_media_anual"]))
        self.assertTrue(pd.isna(out.loc[2001, "preco_nominal_media_anual_lag1"]))

    def test_indice_faltante_preserva_nominal_mas_nao_real(self):
        indice = indice_teste().loc[lambda x: x.data.ne(pd.Timestamp("2000-12-01"))]
        out = anualizar_precos(precos_teste(), indice).set_index("ano")
        self.assertEqual(out.loc[2000, "preco_nominal_media_anual"], 106.5)
        self.assertTrue(pd.isna(out.loc[2000, "preco_real_usd2024_media_anual"]))

    def test_duplicata_mensal_nao_e_media(self):
        base = precos_teste()
        extra = base.iloc[[0]].assign(data="1999-01-15")
        with self.assertRaises(ValueError):
            anualizar_precos(pd.concat([base, extra]))

    def test_ipca_nao_deflaciona_usd(self):
        indice = indice_teste()
        indice.attrs["metadados"] = {"moeda": "BRL"}
        with self.assertRaises(ValueError):
            anualizar_precos(precos_teste(), indice)

    def test_zero_e_negativo_ficam_sinalizados_sem_log(self):
        base = precos_teste()
        base.loc[base.data.eq("2000-01-01"), "preco_nominal"] = 0
        base.loc[base.data.eq("2001-01-01"), "preco_nominal"] = -1
        out = anualizar_precos(base).set_index("ano")
        self.assertEqual(out.loc[2000, "meses_preco_zero"], 1)
        self.assertEqual(out.loc[2001, "meses_preco_negativo"], 1)
        self.assertTrue(pd.isna(out.loc[2000, "ln_preco_nominal_media_anual"]))
        self.assertTrue(pd.isna(out.loc[2001, "preco_nominal_media_anual"]))


class CapacidadeTest(unittest.TestCase):
    def test_historico_cobertura_e_ausencia(self):
        linhas = []
        for codigo, n, valor in (("A", 7, 2000), ("B", 6, 1000), ("C", 10, 3000)):
            for ano in range(1991, 1991 + n):
                linhas.append({"codigo_ibge": codigo, "ano": ano, "produto": "soja",
                               "rendimento_medio_kg_ha": valor, "area_colhida_ha": 100})
        linhas.append({"codigo_ibge": "D", "ano": 2010, "produto": "soja",
                       "rendimento_medio_kg_ha": 4000, "area_colhida_ha": 100})
        out = produtividade_historica(pd.DataFrame(linhas)).set_index("codigo_ibge")
        self.assertEqual(out.loc["A", "media_historica_kg_ha"], 2000)
        self.assertTrue(pd.isna(out.loc["B", "media_historica_kg_ha"]))
        self.assertEqual(out.loc["D", "anos_validos"], 0)
        self.assertTrue(pd.isna(out.loc["D", "media_historica_kg_ha"]))
        self.assertTrue(out.flag_geografia_historica_pendente.all())
        self.assertAlmostEqual(out.capacidade_z.mean(), 0)
        self.assertAlmostEqual(out.capacidade_z.std(), 1)

    def test_rendimento_sem_area_positiva_nao_e_baseline(self):
        base = pd.DataFrame({"codigo_ibge": ["A"] * 10, "ano": range(1991, 2001),
                             "produto": ["soja"] * 10, "rendimento_medio_kg_ha": [0] * 10,
                             "area_colhida_ha": [0] * 10})
        out = produtividade_historica(base)
        self.assertEqual(out.anos_validos.iloc[0], 0)
        self.assertTrue(pd.isna(out.media_historica_kg_ha.iloc[0]))

    def test_gaez_z_por_cenario_e_indice_nao_rendimento(self):
        base = pd.DataFrame({"codigo_ibge": ["A", "B", "C", "A", "B", "C"],
                             "variavel_raster": ["sxHr0_soy"] * 3 + ["yxHr0_soy"] * 3,
                             "valor_medio": [1000, 2000, 3000, 4000, 4000, 4000]})
        out = preparar_gaez(base)
        sx = out.loc[out.tipo_capacidade.eq("aptidao")]
        yx = out.loc[out.tipo_capacidade.eq("rendimento_potencial")]
        np.testing.assert_allclose(sx.aptidao_0_1, [.1, .2, .3])
        np.testing.assert_allclose(sx.capacidade_z, [-1, 0, 1])
        self.assertTrue(yx.aptidao_0_1.isna().all())
        self.assertTrue(yx.capacidade_z.isna().all())
        self.assertTrue(out.flag_temporalidade_pendente.all())


class ChuvaTest(unittest.TestCase):
    @staticmethod
    def chuva():
        return pd.DataFrame([{"codigo_ibge": "A", "ano": ano, "mes": mes,
                              "precip_mm": float(ano - 1980), "fracao_pixels_validos": 1.0}
                             for ano in range(1981, 2025) for mes in range(1, 13)])

    def test_referencia_previa_exata_e_alternativas_preservadas(self):
        out = anualizar_chuva(self.chuva()).set_index("ano")
        esperado = np.arange(1, 21) * 12
        self.assertEqual(out.loc[2001, "precip_mm_anual"], 252)
        self.assertEqual(out.loc[2001, "media_1981_2000"], esperado.mean())
        self.assertAlmostEqual(out.loc[2001, "precip_zscore_1981_2000"],
                               (252 - esperado.mean()) / esperado.std(ddof=1))
        self.assertIn("precip_zscore_1991_2020", out)

    def test_zero_chuva_e_valido_e_mes_ausente_nao_e_zero(self):
        base = self.chuva()
        base.loc[base.ano.eq(2024), "precip_mm"] = 0
        base = base.loc[~(base.ano.eq(2023) & base.mes.eq(12))]
        out = anualizar_chuva(base).set_index("ano")
        self.assertEqual(out.loc[2024, "precip_mm_anual"], 0)
        self.assertTrue(pd.isna(out.loc[2023, "precip_mm_anual"]))

    def test_cobertura_espacial_e_historica(self):
        base = self.chuva()
        base.loc[base.ano.eq(1981) & base.mes.eq(1), "fracao_pixels_validos"] = .5
        out = anualizar_chuva(base).set_index("ano")
        self.assertTrue(pd.isna(out.loc[1981, "precip_mm_anual"]))
        self.assertTrue(out.precip_anomaly_1981_2000.isna().all())
        self.assertEqual(out.loc[2001, "count_1981_2000"], 19)

    def test_cobertura_espacial_desconhecida_nao_e_completa(self):
        out = anualizar_chuva(self.chuva().drop(columns="fracao_pixels_validos"))
        self.assertTrue(out.precip_mm_anual.isna().all())


class InteracaoTest(unittest.TestCase):
    def test_interacao_usa_t_menos_um_e_cenarios_separados(self):
        precos = anualizar_precos(precos_teste(), indice_teste())
        gaez = preparar_gaez(pd.DataFrame({"codigo_ibge": ["A", "B", "A", "B"],
                     "variavel_raster": ["sxHr0_soy", "sxHr0_soy", "yxHr0_soy", "yxHr0_soy"],
                     "valor_medio": [1000, 2000, 3000, 5000]}))
        out = criar_interacoes(precos, gaez=gaez)
        self.assertFalse(out.duplicated(["codigo_ibge", "ano", "produto", "cenario_capacidade"]).any())
        row = out.loc[out.ano.eq(2001)].iloc[0]
        esperado = precos.loc[precos.ano.eq(2000), "ln_preco_real_usd2024_media_anual"].iloc[0] * row.capacidade_z
        self.assertAlmostEqual(row.interacao_ln_preco_real_usd2024_media_anual_lag1_capacidade_z, esperado)
        self.assertEqual(out.cenario_capacidade.nunique(), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
