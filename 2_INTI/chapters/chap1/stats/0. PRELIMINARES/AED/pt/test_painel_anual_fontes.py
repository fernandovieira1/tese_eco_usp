"""Testes do painel montado exclusivamente a partir dos derivados existentes."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from painel_anual_fontes import (
    ADIADAS, NOMES, PASTA_DERIVADOS, carregar_fontes, construir_desde_fontes,
    construir_grade, hash_arquivo, juntar, preparar_blocos,
)


RAIZ = Path(__file__).resolve().parents[6]


class TesteLeituraProtegida(unittest.TestCase):
    """Arquivos artificiais: corrupção deve ser recusada antes de usá-los."""

    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.raiz = Path(self.temporario.name)
        for nome in NOMES:
            pasta = self.raiz / PASTA_DERIVADOS / nome
            pasta.mkdir(parents=True)
            csv = pasta / 'amostra.csv'
            csv.write_text('ano,valor\n2001,1\n', encoding='utf-8')
            manifesto = {'nome': nome, 'status': 'adiada_conforme_plano' if nome in ADIADAS
                         else 'construida_com_ressalvas', 'arquivos': {'amostra': {
                             'arquivo': str(csv.relative_to(self.raiz)),
                             'sha256': hash_arquivo(csv), 'linhas': 1, 'colunas': ['ano', 'valor']}}}
            (pasta / 'manifesto.json').write_text(json.dumps(manifesto), encoding='utf-8')

    def mudar_manifesto(self, funcao):
        path = self.raiz / PASTA_DERIVADOS / NOMES[0] / 'manifesto.json'
        manifesto = json.loads(path.read_text(encoding='utf-8'))
        funcao(manifesto)
        path.write_text(json.dumps(manifesto), encoding='utf-8')

    def test_hash_divergente_interrompe(self):
        csv = self.raiz / PASTA_DERIVADOS / NOMES[0] / 'amostra.csv'
        csv.write_text('ano,valor\n2001,2\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'SHA256 divergente'):
            carregar_fontes(self.raiz)

    def test_contagem_divergente_interrompe(self):
        self.mudar_manifesto(lambda m: m['arquivos']['amostra'].update(linhas=2))
        with self.assertRaisesRegex(ValueError, 'Esquema/contagem'):
            carregar_fontes(self.raiz)

    def test_colunas_divergentes_interrompem(self):
        self.mudar_manifesto(lambda m: m['arquivos']['amostra'].update(colunas=['ano', 'outra']))
        with self.assertRaisesRegex(ValueError, 'Esquema/contagem'):
            carregar_fontes(self.raiz)

    def test_caminho_fora_da_pasta_interrompe(self):
        self.mudar_manifesto(lambda m: m['arquivos']['amostra'].update(arquivo='fora.csv'))
        with self.assertRaisesRegex(ValueError, 'Caminho fora'):
            carregar_fontes(self.raiz)

    def test_mudanca_status_requer_revisao(self):
        self.mudar_manifesto(lambda m: m.update(status='pendente_insumo'))
        with self.assertRaisesRegex(ValueError, 'Situação mudou'):
            carregar_fontes(self.raiz)


class TestePainelDerivado(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fontes, cls.inventario = carregar_fontes(RAIZ)
        cls.painel, cls.blocos, cls.rastreio = construir_desde_fontes(cls.fontes)

    def fonte_modificada(self, nome, tabela, alteracao):
        fontes = self.fontes.copy()
        fontes[nome] = self.fontes[nome].copy()
        fontes[nome]['tabelas'] = self.fontes[nome]['tabelas'].copy()
        base = fontes[nome]['tabelas'][tabela].copy()
        fontes[nome]['tabelas'][tabela] = alteracao(base)
        return fontes

    def test_igualdade_exata_ao_painel_vigente(self):
        referencia = pd.read_csv(
            RAIZ / PASTA_DERIVADOS / 'painel_candidato_2001_2024_141.csv',
            dtype={'codigo_ibge': 'string', 'y_colecao': 'string',
                   'y_malha': 'string', 'y_mascara_id': 'string'},
            float_precision='round_trip', low_memory=False,
        )
        pd.testing.assert_frame_equal(self.painel, referencia, check_exact=True, check_dtype=False)

    def test_25_fontes_48_tabelas_e_exclusoes_explicitas(self):
        self.assertEqual(len(self.fontes), 25)
        self.assertEqual(sum(len(x['tabelas']) for x in self.fontes.values()), 48)
        self.assertEqual(sum(self.inventario.status == 'adiada_conforme_plano'), 4)
        diagnostico = self.inventario.set_index('nome').loc['x3c_infracoes', 'papel_painel']
        self.assertIn('fora da matriz', diagnostico)
        usados = {n for b in self.blocos for n, _ in b['origens']}
        self.assertFalse(usados & ADIADAS)
        self.assertNotIn('x3c_infracoes', usados)
        self.assertEqual(len(usados), 20)

    def test_rastreabilidade_cobre_todas_colunas(self):
        self.assertEqual(list(self.rastreio.coluna_painel), list(self.painel.columns))
        self.assertFalse(self.rastreio.coluna_painel.duplicated().any())
        self.assertTrue(self.rastreio.unidade.str.len().gt(0).all())
        unidades = self.rastreio.set_index('coluna_painel').unidade
        self.assertEqual(unidades['capacidade_valor__milho__gaez_sxHr0_mze'], 'índice GAEZ (0–10.000)')
        self.assertEqual(unidades['capacidade_valor__milho__gaez_yxHr0_mze'], 'kg de matéria seca/ha')

    def test_grade_completa_nao_substitui_ausencia_por_zero(self):
        self.assertEqual(self.painel.shape, (3384, 296))
        self.assertEqual(self.painel.codigo_ibge.nunique(), 141)
        self.assertTrue(self.painel.groupby('codigo_ibge').ano.nunique().eq(24).all())
        self.assertEqual(self.painel.conversao_ha__agricultura.isna().sum(), 612)
        self.assertEqual(self.painel.conversao_ha__agricultura.eq(0).sum(), 265)

    def test_chave_duplicada_nao_multiplica_painel(self):
        fontes = self.fonte_modificada('x4_pecuaria', 'rebanho',
                                       lambda b: pd.concat([b, b.iloc[:1]], ignore_index=True))
        with self.assertRaisesRegex(ValueError, 'nao unica'):
            preparar_blocos(fontes)

    def test_municipio_fora_da_referencia_interrompe(self):
        def alterar(base):
            base.loc[0, 'codigo_ibge'] = '5199999'
            return base
        fontes = self.fonte_modificada('x4_pecuaria', 'rebanho', alterar)
        with self.assertRaisesRegex(ValueError, 'Município fora'):
            preparar_blocos(fontes)

    def test_ano_fora_do_recorte_interrompe(self):
        def alterar(base):
            base.loc[0, 'ano'] = 2025
            return base
        fontes = self.fonte_modificada('x4_pecuaria', 'rebanho', alterar)
        with self.assertRaisesRegex(ValueError, 'Ano fora'):
            preparar_blocos(fontes)

    def test_fontes_redundantes_divergentes_nao_sao_descartadas(self):
        def alterar(base):
            base.loc[0, 'precip_mm_anual'] += 1
            return base
        fontes = self.fonte_modificada('x8_chuvaa', 'chuva_painel', alterar)
        with self.assertRaisesRegex(ValueError, 'Valores divergentes'):
            preparar_blocos(fontes)

    def test_coluna_repetida_nao_ganha_sufixo_silencioso(self):
        bloco = self.blocos[0]
        unido = juntar(construir_grade(self.fontes), bloco['tabela'], bloco['chaves'])
        with self.assertRaisesRegex(ValueError, 'Colunas já presentes'):
            juntar(unido, bloco['tabela'], bloco['chaves'])

    def test_fontes_continuam_com_os_hashes_de_origem(self):
        for fonte in self.fontes.values():
            for meta in fonte['manifesto']['arquivos'].values():
                path = RAIZ / Path(meta['arquivo'].replace('\\', '/'))
                self.assertEqual(hash_arquivo(path), meta['sha256'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
