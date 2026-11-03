"""Testes dos contratos que evitam mistura de fontes e inflação do painel."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from construir_painel import abrir_colunas, juntar, preparar_y_painel
from harmonizacao import validar_insumos_y
from harmonizacao_comum import defasar_ano, exportar_resultado


class ContratosPainelTests(unittest.TestCase):
    def test_y_painel_preserva_denominador_cobertura_e_ausencias(self):
        base = pd.DataFrame({'codigo_ibge': ['a', 'a'], 'ano': [2001, 2001],
                             'destino': ['agricultura', 'pastagem'], 'conversao_ha': [np.nan, np.nan],
                             'taxa_conversao': [np.nan, np.nan]}).assign(
            colecao='10.1', malha='IBGE_MT_2023_141', mascara_id='m', area_total_ha=100.,
            area_valida_par_ha=99., area_nao_valida_par_ha=1., nativa_inicial_ha=50.,
            cobertura_completa=False, fracao_area_valida_par=.99,
            flag_denominador_zero=False, flag_denominador_ausente=False)
        painel = preparar_y_painel(base)
        self.assertEqual(len(painel), 1)
        self.assertFalse(painel.iloc[0].y_cobertura_completa)
        self.assertEqual(painel.iloc[0].y_nativa_inicial_ha, 50.)
        self.assertTrue(pd.isna(painel.iloc[0]['conversao_ha__agricultura']))
        base.loc[1, 'mascara_id'] = 'outra'
        with self.assertRaises(ValueError):
            preparar_y_painel(base)

    def test_duas_fontes_da_colecao_errada_nao_validam_y(self):
        grade = pd.DataFrame({'codigo_ibge': ['a'], 'ano': [2001]})
        fonte = grade.assign(colecao='10.0', malha='IBGE_MT_2023_141')
        with self.assertRaisesRegex(ValueError, '10.1'):
            validar_insumos_y(fonte, fonte, grade)

    def test_cobertura_parcial_nao_vira_insumo_completo(self):
        grade = pd.DataFrame({'codigo_ibge': ['a', 'b'], 'ano': [2001, 2001]})
        fonte = grade.iloc[:1].assign(colecao='10.1', malha='IBGE_MT_2023_141')
        with self.assertRaisesRegex(ValueError, 'incompleta'):
            validar_insumos_y(fonte, fonte, grade)

    def test_grade_correspondente_aceita_zero_linhas_de_transicao(self):
        grade = pd.DataFrame({'codigo_ibge': ['a'], 'ano': [2001]})
        cobertura = grade.assign(colecao='10.1', malha='IBGE_MT_2023_141')
        # A matriz vazia só poderá ser validada fisicamente pela função de terra.
        validar_insumos_y(cobertura.iloc[:0], cobertura, grade)

    def test_defasagem_nao_pula_lacuna(self):
        base = pd.DataFrame({'codigo_ibge': ['a', 'a'], 'ano': [2000, 2002], 'valor': [3., 7.]})
        r = defasar_ano(base, ['valor'])
        self.assertTrue(r.valor_lag1.isna().all())

    def test_juncao_estatica_preserva_linhas_e_ausencias(self):
        painel = pd.DataFrame({'codigo_ibge': ['a', 'a', 'b'], 'ano': [2001, 2002, 2001]})
        atributo = pd.DataFrame({'codigo_ibge': ['a'], 'capacidade': [5.]})
        r = juntar(painel, atributo, ['codigo_ibge'])
        self.assertEqual(len(r), 3)
        self.assertTrue(pd.isna(r.iloc[-1].capacidade))
        with self.assertRaises(ValueError):
            juntar(painel, pd.concat([atributo, atributo]), ['codigo_ibge'])

    def test_pivo_nao_oculta_duplicatas_por_media(self):
        base = pd.DataFrame({'codigo_ibge': ['a', 'a'], 'ano': [2001, 2001],
                             'produto': ['soja', 'soja'], 'valor': [2., 4.]})
        with self.assertRaises(ValueError):
            abrir_colunas(base, ['codigo_ibge', 'ano'], ['produto'], ['valor'])

    def test_exportacao_preserva_metadados_terra_e_na(self):
        base = pd.DataFrame({'codigo_ibge': ['a', 'b'], 'valor': [0., np.nan]})
        base.attrs = {'colecao': '10.1', 'classes_nativas': [3, 4]}
        r = {'nome': 'teste', 'status': 'candidato', 'principal': 'terra', 'tabelas': {'terra': base},
             'parametros': {}, 'pendencias': [], 'dicionario': [{'coluna': 'valor', 'unidade': 'ha'}]}
        with tempfile.TemporaryDirectory() as temp:
            pasta = exportar_resultado(r, Path(temp))
            manifest = json.loads((pasta/'manifesto.json').read_text(encoding='utf-8'))
            self.assertEqual(manifest['arquivos']['terra']['metadados']['colecao'], '10.1')
            saved = pd.read_csv(pasta/'terra.csv')
            self.assertEqual(saved.iloc[0].valor, 0.)
            self.assertTrue(pd.isna(saved.iloc[1].valor))


if __name__ == '__main__':
    unittest.main(verbosity=2)
