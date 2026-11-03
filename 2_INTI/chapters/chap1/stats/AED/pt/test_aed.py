"""Testes sintéticos das salvaguardas que mudam o significado das medidas.

Executar: python -m unittest discover -s 2_INTI/chapters/chap1/stats/AED/pt -p test_aed.py -v
"""

import contextlib
import io
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from aed_features import feature_code
from aed_support import assert_unique, harmonizar_codigos


def executar_fase6(nome, base, bases=None):
    """Executa a mesma célula incorporada no notebook, sem interface gráfica."""
    namespace = {
        "pd": pd,
        "np": np,
        "df": base.copy(),
        "painel": base.loc[base["ano"].between(2001, 2024)].copy() if "ano" in base else base.copy(),
        "bases": bases if bases is not None else [base.copy()],
        "assert_unique": assert_unique,
        "display": lambda *args, **kwargs: None,
    }
    with contextlib.redirect_stdout(io.StringIO()):
        exec(compile(feature_code(nome), f"<{nome}:fase6>", "exec"), namespace)
    return namespace


class TaxasConversaoTests(unittest.TestCase):
    def setUp(self):
        self.denominador = pd.DataFrame({
            "codigo_ibge": ["a", "b", "c"], "ano": [2001] * 3,
            "native_veg_ha_lag1": [100.0, 0.0, np.nan],
        })
        self.conversao = pd.DataFrame({
            "codigo_ibge": ["a", "a", "b", "c", "d"], "ano": [2001] * 5,
            "destino": ["agricultura", "pastagem", "pastagem", "pastagem", "pastagem"],
            "area_conv_ha": [25.0, 10.0, 0.0, 0.0, 1.0],
        })
        self.namespace = executar_fase6("Y_tx-conv", self.denominador)

    def test_destinos_separados_e_denominador_zero_ou_ausente(self):
        resultado = self.namespace["construir_taxas"](self.conversao, self.denominador, True)
        self.assertAlmostEqual(resultado.loc[0, "taxa_conv"], 0.25)
        self.assertAlmostEqual(resultado.loc[1, "taxa_conv"], 0.10)
        self.assertTrue(resultado.loc[2:, "taxa_conv"].isna().all())
        self.assertTrue(resultado.loc[2, "flag_denominador_nulo"])
        self.assertTrue(resultado.loc[3:, "flag_denominador_ausente"].all())
        self.assertEqual(resultado.loc[4, "_merge"], "left_only")
        largo = self.namespace["abrir_colunas"](
            resultado, ["codigo_ibge", "ano"], "destino", "taxa_conv",
        )
        self.assertTrue({"agricultura", "pastagem"}.issubset(largo.columns))
        self.assertEqual(len(largo), 4)

    def test_zero_registrado_com_denominador_positivo_e_taxa_invalida_visivel(self):
        conversao = self.conversao.iloc[:2].copy()
        conversao["area_conv_ha"] = [0.0, 120.0]
        resultado = self.namespace["construir_taxas"](conversao, self.denominador, True)
        self.assertEqual(resultado.loc[0, "taxa_conv"], 0.0)
        self.assertAlmostEqual(resultado.loc[1, "taxa_conv"], 1.2)
        self.assertTrue(resultado.loc[1, "flag_taxa_fora_0_1"])

    def test_exige_geografia_validada_e_recusa_duplicatas(self):
        construir = self.namespace["construir_taxas"]
        with self.assertRaisesRegex(ValueError, "geografia"):
            construir(self.conversao, self.denominador)
        duplicada = pd.concat([self.conversao, self.conversao.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "repetida"):
            construir(duplicada, self.denominador, True)

    def test_medida_nao_construida_fica_none(self):
        self.assertIsNone(self.namespace["features"])


class AgregacaoMensalTests(unittest.TestCase):
    @staticmethod
    def precos():
        linhas = []
        for ano, meses, valor in [(2001, 12, 10.0), (2002, 11, 20.0), (2003, 12, 0.0)]:
            for mes in range(1, meses + 1):
                linhas.append({
                    "data": pd.Timestamp(ano, mes, 1), "variavel": "price_soja",
                    "preco_nominal": valor,
                })
        # Doze linhas com um valor ausente também formam um ano incompleto.
        for mes in range(1, 13):
            linhas.append({
                "data": pd.Timestamp(2004, mes, 1), "variavel": "price_soja",
                "preco_nominal": np.nan if mes == 12 else 30.0,
            })
        return pd.DataFrame(linhas)

    def test_preco_usa_media_com_doze_meses_e_preserva_zero(self):
        base = self.precos()
        original = base.copy(deep=True)
        resultado = executar_fase6("x1_psoja-pmilho", base)["features"].set_index("ano")
        self.assertEqual(resultado.loc[2001, "price_soja"], 10.0)
        self.assertTrue(pd.isna(resultado.loc[2002, "price_soja"]))
        self.assertEqual(resultado.loc[2003, "price_soja"], 0.0)
        self.assertTrue(pd.isna(resultado.loc[2004, "price_soja"]))
        assert_frame_equal(base, original)

    def test_preco_mes_duplicado_nao_e_compensado_por_media(self):
        base = self.precos()
        base = pd.concat([base, base.iloc[[0]]], ignore_index=True)
        self.assertIsNone(executar_fase6("x1_psoja-pmilho", base)["features"])

    @staticmethod
    def chuva():
        linhas = []
        for ano, meses, valor in [(2001, 12, 10.0), (2002, 11, 20.0), (2003, 12, 0.0)]:
            for mes in range(1, meses + 1):
                linhas.append({
                    "codigo_ibge": "a", "ano": ano, "mes": mes,
                    "precip_mm": valor, "fracao_pixels_validos": 1.0,
                })
        for mes in range(1, 13):
            linhas.append({
                "codigo_ibge": "a", "ano": 2004, "mes": mes,
                "precip_mm": np.nan if mes == 12 else 30.0, "fracao_pixels_validos": 1.0,
            })
        return pd.DataFrame(linhas)

    def test_chuva_usa_soma_com_doze_meses_e_preserva_zero(self):
        resultado = executar_fase6("x8_chuva", self.chuva())["features"].set_index("ano")
        self.assertEqual(resultado.loc[2001, "precip_mm_anual"], 120.0)
        self.assertTrue(pd.isna(resultado.loc[2002, "precip_mm_anual"]))
        self.assertEqual(resultado.loc[2003, "precip_mm_anual"], 0.0)
        self.assertTrue(pd.isna(resultado.loc[2004, "precip_mm_anual"]))

    def test_chuva_mes_duplicado_ou_invalido_impede_soma(self):
        base = self.chuva()
        duplicada = pd.concat([base, base.iloc[[0]]], ignore_index=True)
        self.assertIsNone(executar_fase6("x8_chuva", duplicada)["features"])
        base.loc[0, "mes"] = 13
        self.assertIsNone(executar_fase6("x8_chuva", base)["features"])


class HistoricoTests(unittest.TestCase):
    def setUp(self):
        self.base = pd.DataFrame({
            "codigo_ibge": ["a", "a", "a", "b", "b", "c"],
            "ano": [1999, 2000, 2001, 1999, 2000, 2001],
            "produto": ["Soja"] * 6,
            "rendimento_medio_kg_ha": [10.0, 20.0, 9000.0, np.nan, 30.0, 2000.0],
        })
        self.construir = executar_fase6("x2a_hprodsoj-hprodmil", self.base)["produtividade_historica"]

    def test_nao_usa_pos2000_e_nao_preenche_ausencia_com_zero(self):
        resultado = self.construir(self.base, 1999, 2000, 1, True).set_index("codigo_ibge")
        self.assertEqual(resultado.loc["a", "media_historica_kg_ha"], 15.0)
        self.assertEqual(resultado.loc["b", "media_historica_kg_ha"], 30.0)
        self.assertEqual(resultado.loc["b", "anos_validos"], 1)
        self.assertEqual(resultado.loc["b", "fracao_anos_validos"], 0.5)
        self.assertTrue(pd.isna(resultado.loc["c", "media_historica_kg_ha"]))

    def test_minimo_anos_e_janela_nao_podem_ser_ignorados(self):
        resultado = self.construir(self.base, 1999, 2000, 2, True).set_index("codigo_ibge")
        self.assertTrue(pd.isna(resultado.loc["b", "media_historica_kg_ha"]))
        with self.assertRaisesRegex(ValueError, "anterior a 2001"):
            self.construir(self.base, 1999, 2001, 2, True)
        with self.assertRaisesRegex(ValueError, "limites"):
            self.construir(self.base, 1999, 2000, 2)


class HarmonizacaoTests(unittest.TestCase):
    def setUp(self):
        self.base = pd.DataFrame({
            "codigo_ibge": ["a", "b"], "ano": [2001, 2001], "valor": [10.0, 20.0],
        })
        self.mapa = pd.DataFrame({
            "codigo_ibge": ["a", "b"], "ano": [2001, 2001], "codigo_harmonizado": ["x", "y"],
        })

    def test_mapa_um_para_um_preserva_linhas_valores_e_codigo_original(self):
        original = self.base.copy(deep=True)
        resultado = harmonizar_codigos(self.base, self.mapa, ["codigo_ibge", "ano"])
        self.assertEqual(resultado["codigo_ibge"].tolist(), ["x", "y"])
        self.assertEqual(resultado["codigo_ibge_original"].tolist(), ["a", "b"])
        self.assertEqual(resultado["valor"].tolist(), [10.0, 20.0])
        assert_frame_equal(self.base, original)

    def test_recusa_duplicidade_na_origem_do_mapa(self):
        duplicado = pd.concat([self.mapa, self.mapa.iloc[[0]]], ignore_index=True)
        with self.assertRaisesRegex(ValueError, "repetida"):
            harmonizar_codigos(self.base, duplicado, ["codigo_ibge", "ano"])

    def test_recusa_colisao_de_destinos_sem_pesos_territoriais(self):
        colisao = self.mapa.copy()
        colisao["codigo_harmonizado"] = "x"
        with self.assertRaisesRegex(ValueError, "repetida"):
            harmonizar_codigos(self.base, colisao, ["codigo_ibge", "ano"])

    def test_recusa_mapa_sem_correspondencia(self):
        with self.assertRaisesRegex(ValueError, "Falta correspondência"):
            harmonizar_codigos(self.base, self.mapa.iloc[:1], ["codigo_ibge", "ano"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
