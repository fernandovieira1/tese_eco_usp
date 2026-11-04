"""Testes dos significados de contagem, localização, deflação e tempo.

Executar pelo ambiente documentado:
python -m unittest discover -s 2_INTI/chapters/chap1/stats/AED/pt -p test_harmonizacao_instituicoes.py -v
"""

import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal

from harmonizacao_instituicoes import (
    adicionar_defasagens_calendario,
    construir_instituicoes,
    deflacionar_autos,
    diagnosticar_pendencias,
    preparar_autos,
)


M1, M2 = "5100102", "5100201"


def eventos_exemplo():
    return pd.DataFrame({
        "SEQ_AUTO_INFRACAO": ["1", "2", "3", "4", "5", "6"],
        "DAT_HORA_AUTO_INFRACAO": ["2000-12-01", "2001-01-15", "2001-02-15", "2001-03-15", "2002-05-01", "2004-05-01"],
        "DT_FATO_INFRACIONAL": [None, "1998-02-01", None, None, None, None],
        "codigo_ibge": [M1, M1, M1, M1, M2, M2],
        "TIPO_INFRACAO": ["Flora", "Flora", "Flora", None, "Fauna", "Fauna"],
        "INFRACAO_AREA": ["Desmatamento", "Desmatamento", "Desmatamento e Queimada", None, "Outros", "Outros"],
        "DS_SIT_AUTO_AIE": [None] * 6,
        "SIT_CANCELADO": ["N", "S", "N", "N", "N", "N"],
        "valor_multa_nominal": [50, 100, 100, None, 0, 0],
    })


def geocod_exemplo():
    # O auto2 tem divergência territorial, o auto4 não tem coordenada associada.
    return pd.DataFrame({
        "SEQ_AUTO_INFRACAO": ["1", "2", "3", "5", "6"],
        "codigo_ibge_espacial": [M1, M2, M1, M2, M2],
        "geografia_referencia": ["IBGE_2023_141"] * 5,
    })


def ipca_exemplo():
    return pd.DataFrame({"data": pd.to_datetime(["2000-12-01", "2001-01-01", "2001-02-01", "2001-03-01", "2002-05-01", "2004-05-01", "2024-12-01"]),
                         "indice_precos": [50, 50, 100, 100, 100, 100, 100]})


def executar(eventos=None, geo=None, **kwargs):
    return construir_instituicoes(eventos_exemplo() if eventos is None else eventos,
                                  geocod_exemplo() if geo is None else geo, [M1, M2],
                                  ipca=ipca_exemplo(), ano_inicio=2001, ano_fim=2004, **kwargs)


class InstituicoesTests(unittest.TestCase):
    def test_lavratura_preserva_status_desconhecido_e_cancelamento_atual(self):
        tabela = executar()["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertEqual(tabela.loc[(M1, 2001), "n_autos_flora"], 2)
        self.assertEqual(tabela.loc[(M1, 2001), "n_cancelados_atuais"], 1)
        self.assertEqual(tabela.loc[(M1, 2001), "n_status_atual_ausente"], 3)
        self.assertTrue(tabela.loc[(M1, 2001), "flag_contagem_flora_parcial"])

    def test_deflacao_por_mes_antes_de_somar(self):
        tabela = executar()["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        # 100×100/50 + 100×100/100 = 300, não 200 deflacionado pela média75.
        self.assertEqual(tabela.loc[(M1, 2001), "multas_flora_reais_observadas"], 300)
        self.assertEqual(tabela.loc[(M1, 2001), "multas_flora_nominais_observadas"], 200)

    def test_ausencia_nao_vira_zero_e_zero_exige_tema_conhecido(self):
        tabela = executar()["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertTrue(pd.isna(tabela.loc[(M1, 2002), "n_autos_flora"]))
        self.assertTrue(tabela.loc[(M1, 2002), "flag_sem_registro_identificado"])
        self.assertEqual(tabela.loc[(M2, 2002), "n_autos_flora"], 0)
        e = eventos_exemplo().iloc[[4]].copy()
        e["TIPO_INFRACAO"] = None
        tabela = executar(eventos=e)["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertTrue(pd.isna(tabela.loc[(M2, 2002), "n_autos_flora"]))

    def test_lag_aproveita_2000_e_nao_atravessa_lacunas(self):
        tabela = executar()["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertEqual(tabela.loc[(M1, 2001), "n_autos_flora_lag1"], 1)
        self.assertEqual(tabela.loc[(M1, 2002), "n_autos_flora_lag1"], 2)
        self.assertTrue(pd.isna(tabela.loc[(M2, 2004), "n_autos_flora_lag1"]))
        irregular = pd.DataFrame({"codigo_ibge": [M1, M1], "ano": [2001, 2003], "v": [8, 9]})
        self.assertTrue(pd.isna(adicionar_defasagens_calendario(irregular, ["v"]).iloc[1]["v_lag1"]))

    def test_localizacoes_sao_alternativas_e_divergencia_exclui_na(self):
        saidas = executar()
        espacial = saidas["instituicoes_espacial"].set_index(["codigo_ibge", "ano"])
        self.assertEqual(espacial.loc[(M1, 2001), "n_autos_flora"], 1)
        self.assertEqual(espacial.loc[(M2, 2001), "n_autos_flora"], 1)
        qualidade = saidas["qualidade_geocodificacao"].set_index("ano")
        self.assertEqual(qualidade.loc[2001, "n_comparaveis"], 2)
        self.assertEqual(qualidade.loc[2001, "taxa_divergencia"], 0.5)
        self.assertEqual(qualidade.loc[2001, "n_ids_sem_espacial_valido"], 1)

    def test_identidades_conflitantes_falham_duplicatas_exatas_nao_duplicam(self):
        e = eventos_exemplo()
        exato = pd.concat([e, e.iloc[[1]]], ignore_index=True)
        self.assertEqual(preparar_autos(exato, geocod_exemplo(), [M1, M2]).shape[0], len(e))
        conflito = e.iloc[[1]].copy()
        conflito["valor_multa_nominal"] = 999
        with self.assertRaisesRegex(ValueError, "conflitantes"):
            preparar_autos(pd.concat([e, conflito]), geocod_exemplo(), [M1, M2])

    def test_sem_id_nao_e_contado_e_sinaliza_cobertura_do_grupo(self):
        e = eventos_exemplo().iloc[[4]].copy()
        adicional = e.copy()
        adicional["SEQ_AUTO_INFRACAO"] = None
        adicional["TIPO_INFRACAO"] = "Flora"
        tabela = executar(eventos=pd.concat([e, adicional]))["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertEqual(tabela.loc[(M2, 2002), "n_autos_observados"], 1)
        self.assertEqual(tabela.loc[(M2, 2002), "n_registros_sem_id"], 1)
        self.assertTrue(pd.isna(tabela.loc[(M2, 2002), "n_autos_flora"]))

    def test_codigo_novo_nao_e_alocado_a_um_pai_arbitrario(self):
        e = eventos_exemplo().iloc[[1]].copy()
        e["codigo_ibge"] = "5101837"
        saidas = executar(eventos=e)
        self.assertTrue(saidas["instituicoes_informada"]["n_autos_observados"].isna().all())
        self.assertEqual(saidas["instituicoes_espacial"]["n_autos_observados"].sum(), 1)
        with self.assertRaisesRegex(ValueError, "Boa Esperança"):
            preparar_autos(e, geocod_exemplo(), [M1, "5101837"])

    def test_nao_aceita_geografia_nao_reconstruida(self):
        g = geocod_exemplo()
        g["geografia_referencia"] = "IBGE_2024_142"
        with self.assertRaisesRegex(ValueError, "IBGE_2023_141"):
            preparar_autos(eventos_exemplo(), g, [M1, M2])

    def test_ipca_sem_base_duplicado_ou_negativo_falha(self):
        autos = preparar_autos(eventos_exemplo(), geocod_exemplo(), [M1, M2])
        with self.assertRaisesRegex(ValueError, "Mês-base"):
            deflacionar_autos(autos, ipca_exemplo().iloc[:-1])
        for ruim in [pd.concat([ipca_exemplo(), ipca_exemplo().iloc[[0]]]),
                     ipca_exemplo().assign(indice_precos=-1), ipca_exemplo().assign(indice_precos=np.inf)]:
            with self.assertRaisesRegex(ValueError, "níveis positivos"):
                deflacionar_autos(autos, ruim)

    def test_ipca_ausente_no_evento_nao_produz_zero(self):
        autos = preparar_autos(eventos_exemplo(), geocod_exemplo(), [M1, M2])
        saida = deflacionar_autos(autos, ipca_exemplo().iloc[[6]])
        self.assertTrue(saida["valor_multa_real"].isna().all())
        self.assertTrue(saida["flag_ipca_ausente"].all())

    def test_soma_parcial_nao_e_inflada_para_total(self):
        e = eventos_exemplo().iloc[[1, 2]].copy()
        e.loc[e["SEQ_AUTO_INFRACAO"].eq("3"), "valor_multa_nominal"] = np.nan
        tabela = executar(eventos=e)["instituicoes_informada"].set_index(["codigo_ibge", "ano"])
        self.assertEqual(tabela.loc[(M1, 2001), "multas_flora_reais_observadas"], 200)
        self.assertTrue(tabela.loc[(M1, 2001), "flag_soma_flora_parcial"])
        self.assertEqual(tabela.loc[(M1, 2001), "n_flora_valores_reais_ausentes"], 1)

    def test_normalizacao_nao_usa_busca_textual_de_crime(self):
        e = eventos_exemplo().iloc[[1]].copy()
        e["TIPO_INFRACAO"] = "  FLORA  "
        e["INFRACAO_AREA"] = "Desmatamento e Queimada"
        e["DES_INFRACAO"] = "transportar madeira"
        out = preparar_autos(e, geocod_exemplo(), [M1, M2])
        self.assertTrue(out.iloc[0]["tema_flora"])
        self.assertTrue(out.iloc[0]["tema_desmatamento"])

    def test_fontes_nao_sao_modificadas_e_metadata_existe(self):
        e, g, indice = eventos_exemplo(), geocod_exemplo(), ipca_exemplo()
        antes = [x.copy(deep=True) for x in [e, g, indice]]
        out = construir_instituicoes(e, g, [M1, M2], ipca=indice, ano_inicio=2001, ano_fim=2004)
        for a, b in zip([e, g, indice], antes):
            assert_frame_equal(a, b)
        self.assertTrue(all("metadados" in tabela.attrs for tabela in out.values()))

    def test_pendencias_nao_transformam_historico_em_fluxo(self):
        h = pd.DataFrame({"SEQ_TAD": ["a", "a", "b"], "DAT_EMBARGO": ["2001-01-01", "2002-01-01", "2001-01-01"]})
        p = diagnosticar_pendencias(h, pd.DataFrame({"SEQ_TAD": ["a", "a", "a"]}))
        self.assertFalse(p["medida_final_construida"].any())
        self.assertEqual(p.iloc[0]["n_ids_distintos_cadastrados"], 2)
        self.assertEqual(p.iloc[0]["n_ids_datas_embargo_conflitantes"], 1)
        self.assertEqual(p.iloc[0]["n_linhas_coordenadas"], 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
