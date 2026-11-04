"""Contraexemplos: repetição, ausência, taxas e amostra comum."""
import unittest
import numpy as np
import pandas as pd
from painel_anual_descritiva import (catalogar, normalizar_tipos, descrever_medidas, resumo_por_fonte,
    amostra_medida, resumo_y, frequencias_qualidade, diagnosticar_amostras)


class TestDescritiva(unittest.TestCase):
    def setUp(self):
        self.painel = pd.DataFrame({
            'codigo_ibge': ['a', 'a', 'a', 'b', 'b', 'b'], 'ano': [2001, 2002, 2003] * 2,
            'preco_real_usd2024_media_anual__soja': [10., 20., 30.] * 2,
            'elevation_mean_m': [100.] * 3 + [200.] * 3,
            'precip_mm_anual': [0., np.nan, 20., 30., 40., 50.],
            'flag_teste': pd.Series([True, False, None, False, None, True], dtype=object),
            'y_colecao': [10.1] * 6,
        })
        rastros = pd.DataFrame({'coluna_painel': self.painel.columns,
                               'notebooks': ['x8_chuva.ipynb'] * len(self.painel.columns),
                               'unidade': [''] * len(self.painel.columns)})
        self.catalogo = catalogar(self.painel, rastros)

    def test_repeticao_nao_inflaciona_n(self):
        resumo = descrever_medidas(self.painel, self.catalogo).set_index('variavel')
        self.assertEqual(resumo.loc['preco_real_usd2024_media_anual__soja', 'n_validos'], 3)
        self.assertEqual(resumo.loc['elevation_mean_m', 'n_validos'], 2)
        self.assertEqual(resumo.loc['elevation_mean_m', 'media'], 150)

    def test_zero_diferente_de_ausencia(self):
        resumo = descrever_medidas(self.painel, self.catalogo).set_index('variavel')
        r = resumo.loc['precip_mm_anual']
        self.assertEqual((r.n_oportunidades, r.n_validos, r.n_ausentes, r.n_zeros), (6, 5, 1, 1))

    def test_numeros_object_nao_sao_omitidos(self):
        self.painel['preco_real_usd2024_media_anual__soja'] = self.painel['preco_real_usd2024_media_anual__soja'].astype(object)
        tratado = normalizar_tipos(self.painel)
        self.assertEqual(str(tratado.flag_teste.dtype), 'boolean')
        self.assertTrue(pd.api.types.is_numeric_dtype(tratado['preco_real_usd2024_media_anual__soja']))
        resumo = descrever_medidas(self.painel, self.catalogo)
        self.assertEqual(len(resumo), 3)

    def test_preco_diferente_no_mesmo_ano_interrompe(self):
        self.painel.loc[3, 'preco_real_usd2024_media_anual__soja'] = 999
        with self.assertRaises(ValueError):
            amostra_medida(self.painel, 'preco_real_usd2024_media_anual__soja', self.catalogo)

    def test_versao_e_booleano_nullable_nao_sao_medidas(self):
        resumo = descrever_medidas(self.painel, self.catalogo)
        self.assertNotIn('y_colecao', set(resumo.variavel))
        self.assertNotIn('flag_teste', set(resumo.variavel))
        flags = frequencias_qualidade(self.painel, self.catalogo).set_index('coluna')
        self.assertEqual(tuple(flags.loc['flag_teste', ['n_true', 'n_false', 'n_ausentes']]), (2, 2, 2))

    def test_rastreia_nome_com_extensao(self):
        resumo = descrever_medidas(self.painel, self.catalogo)
        self.assertEqual(len(resumo_por_fonte(resumo, self.catalogo, 'x8_chuva')), 3)

    def test_taxas_media_vs_razao_mesma_amostra(self):
        painel = pd.DataFrame({'codigo_ibge': ['a', 'b', 'c'], 'ano': [2001] * 3,
                              'y_nativa_inicial_ha': [100., 900., 9000.]})
        for destino in ['agricultura', 'pastagem']:
            painel[f'conversao_ha__{destino}'] = [10., 180., np.nan]
            painel[f'taxa_conversao__{destino}'] = [.1, .2, np.nan]
        resumo = resumo_y(painel)
        self.assertTrue(np.allclose(resumo.taxa_media_simples, .15))
        self.assertTrue(np.allclose(resumo.taxa_razao_das_somas, .19))
        self.assertTrue(resumo.nativa_inicial_mesma_amostra_ha.eq(1000).all())
        self.assertTrue(resumo.n_ausentes.eq(1).all())

    def test_ausencia_total_nao_produz_total_zero(self):
        painel = pd.DataFrame({'codigo_ibge': ['a'], 'ano': [2001], 'y_nativa_inicial_ha': [100.]})
        for destino in ['agricultura', 'pastagem']:
            painel[f'conversao_ha__{destino}'] = np.nan
            painel[f'taxa_conversao__{destino}'] = np.nan
        resumo = resumo_y(painel)
        self.assertTrue(resumo.conversao_observada_ha.isna().all())
        self.assertTrue(resumo.taxa_razao_das_somas.isna().all())

    def test_cobertura_depende_das_colunas_escolhidas(self):
        r = diagnosticar_amostras(self.painel, {'preco': ['preco_real_usd2024_media_anual__soja'],
                                               'chuva': ['precip_mm_anual']})
        self.assertEqual(list(r.n_pares_completos), [6, 5])


if __name__ == '__main__':
    unittest.main()
