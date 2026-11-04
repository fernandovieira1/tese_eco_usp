"""Testes de identidade de áreas, zeros, máscaras e calendário."""
import unittest

import numpy as np
import pandas as pd

from harmonizacao_terra import (
    construir_lotacao, construir_taxas, construir_transicoes, construir_usos,
    defasar_ano_exato,
)
from obter_transicoes_mapbiomas import tabelas_do_resultado


class TerraTests(unittest.TestCase):
    def setUp(self):
        self.ref = pd.DataFrame({"codigo_ibge": ["5100102"]})
        self.classes = pd.DataFrame([
            ["5100102", year, "Cerrado", cls, area]
            for year in [2000, 2001, 2002]
            for cls, area in [(3, 60), (15, 30), (39, 10)]
        ], columns=["codigo_ibge", "ano", "biome", "class_id", "area_ha"])
        common = {"codigo_ibge": "5100102", "ano": 2001, "colecao": "10.1", "malha": "IBGE2023", "mascara_id": "mask1"}
        self.matrix = pd.DataFrame([{**common, "classe_origem": origin, "classe_destino": destiny, "area_ha": area}
                                    for origin, destiny, area in [(3, 3, 50), (3, 15, 8), (3, 39, 2), (15, 15, 40)]])
        self.coverage = pd.DataFrame([{**common, "nativa_inicial_ha": 60, "area_valida_par_ha": 100, "cobertura_completa": True}])

    def test_usos_somas_shares_e_lags(self):
        out = construir_usos(self.classes, self.ref, 2001, 2002)
        self.assertEqual(len(out), 2)
        self.assertEqual(out.iloc[0].nativa_ha_lag1, 60)
        self.assertEqual(out.iloc[0].pastagem_share, .3)
        self.assertEqual(out.iloc[0].agricultura_ha, 10)

    def test_categoria_inteiramente_ausente_no_ano_nao_vira_zero(self):
        partial = self.classes.drop(self.classes.query("ano == 2001 and class_id == 39").index)
        out = construir_usos(partial, self.ref, 2001, 2002)
        self.assertFalse(out.iloc[0].grade_fonte_completa)
        self.assertTrue(pd.isna(out.iloc[0].agricultura_ha))
        self.assertTrue(pd.isna(out.iloc[1].nativa_ha_lag1))

    def test_uso_sem_registro_em_toda_historia_permanece_ausente(self):
        out = construir_usos(self.classes.query("class_id != 39"), self.ref, 2001, 2002)
        self.assertTrue(out.agricultura_ha.isna().all())

    def test_lag_nao_pula_ano(self):
        base = pd.DataFrame({"codigo_ibge": ["5100102"] * 2, "ano": [2000, 2002], "x": [3., 4.]})
        self.assertTrue(defasar_ano_exato(base, ["x"]).x_lag1.isna().all())

    def test_pais_e_filhos_rejeitados(self):
        base = self.classes.copy()
        base.loc[0, "class_id"] = 18
        with self.assertRaises(ValueError):
            construir_usos(base, self.ref)

    def test_duplicatas_rejeitadas(self):
        with self.assertRaises(ValueError):
            construir_usos(pd.concat([self.classes, self.classes.iloc[[0]]]), self.ref)

    def test_lotacao_preserva_zero_e_denominador_nulo(self):
        uses = pd.DataFrame({"codigo_ibge": ["5100102"] * 3, "ano": [2001, 2002, 2003], "pastagem_ha": [10., 0., np.nan]})
        herd = uses[["codigo_ibge", "ano"]].assign(efetivo_bovino=[0., 3., 4.])
        out = construir_lotacao(herd, uses)
        self.assertEqual(out.iloc[0].lotacao_cabecas_ha, 0)
        self.assertTrue(out.lotacao_cabecas_ha.iloc[1:].isna().all())
        self.assertTrue(out.iloc[1].flag_bovinos_sem_pastagem)

    def test_transicoes_reais_e_taxa_mesma_mascara(self):
        out = construir_transicoes(self.matrix, self.coverage).set_index("destino")
        self.assertEqual(out.loc["agricultura", "conversao_ha"], 2)
        self.assertAlmostEqual(out.loc["pastagem", "taxa_conversao"], 8 / 60)

    def test_mascara_divergente_rejeitada(self):
        altered = self.matrix.assign(mascara_id="other")
        with self.assertRaises(ValueError):
            construir_transicoes(altered, self.coverage)

    def test_matriz_incompleta_rejeitada(self):
        with self.assertRaises(ValueError):
            construir_transicoes(self.matrix.iloc[:-1], self.coverage)

    def test_sem_conversao_zero_so_com_matriz_completa(self):
        base = self.matrix.copy()
        base.loc[base.classe_destino.eq(39), "classe_destino"] = 33
        valid = construir_transicoes(base, self.coverage).set_index("destino")
        self.assertEqual(valid.loc["agricultura", "conversao_ha"], 0)
        invalid = construir_transicoes(base, self.coverage.assign(cobertura_completa=False))
        self.assertTrue(invalid.conversao_ha.isna().all())

    def test_denominador_zero_taxa_indefinida(self):
        base = pd.DataFrame({"codigo_ibge": ["5100102"], "ano": [2001], "destino": ["pastagem"], "conversao_ha": [0.], "nativa_inicial_ha": [0.]})
        out = construir_taxas(base)
        self.assertTrue(pd.isna(out.iloc[0].taxa_conversao))
        with self.assertRaises(ValueError):
            construir_taxas(base.assign(conversao_ha=1))

    def test_grafo_gee_resposta_convertida_conserva_areas(self):
        response = {"requisicao": {"codigo_ibge": "5100102", "ano": 2001, "mascara_id": "m1"},
                    "resultado": {"area_total_ha": 100., "area_valida_par_ha": 100., "area_nao_valida_par_ha": 0., "nativa_inicial_ha": 60.,
                                  "groups": [{"transition": 303, "sum": 50.}, {"transition": 315, "sum": 10.}, {"transition": 1515, "sum": 40.}]}}
        matrix, cov = tabelas_do_resultado(response)
        out = construir_transicoes(matrix, cov).set_index("destino")
        self.assertEqual(out.loc["pastagem", "conversao_ha"], 10.)
        response["resultado"]["area_total_ha"] = 101.
        response["resultado"]["area_nao_valida_par_ha"] = 1.
        _, incomplete = tabelas_do_resultado(response)
        self.assertFalse(incomplete.iloc[0].cobertura_completa)

    def test_cobertura_distingue_arredondamento_de_pixel_invalido(self):
        response = {"requisicao": {"codigo_ibge": "5100102", "ano": 2001, "mascara_id": "m1"},
                    "resultado": {"area_total_ha": 399086.1323413696, "area_valida_par_ha": 399086.1320934418,
                                  "area_nao_valida_par_ha": 0., "nativa_inicial_ha": 60., "groups": []}}
        _, cov = tabelas_do_resultado(response)
        self.assertTrue(cov.iloc[0].cobertura_completa)
        # Uma área inválida real, mesmo pequena, não é ignorada pela tolerância.
        response["resultado"]["area_nao_valida_par_ha"] = .0002
        _, cov = tabelas_do_resultado(response)
        self.assertFalse(cov.iloc[0].cobertura_completa)
        response["resultado"]["area_total_ha"] += 10
        with self.assertRaises(ValueError):
            tabelas_do_resultado(response)


if __name__ == "__main__":
    unittest.main()
