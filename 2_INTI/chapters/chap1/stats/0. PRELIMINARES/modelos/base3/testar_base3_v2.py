"""Testes da extensão; não executa modelos nem altera v1."""
import json
import csv
import io
import math
import statistics
import subprocess
import unittest
import construir_base3_v2 as b

class Incremento(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v1=b.ler(b.V1);cls.final=b.ler(b.P/'painel_h1_base3_v2.csv')
        inverse={v:k for k,v in b.mapa_colunas().items()}
        cls.v2=[{inverse[k]:v for k,v in r.items()} for r in cls.final]
        cls.anual=b.ler(b.P/'economia_anual_v2.csv');cls.mensal=b.ler(b.P/'auditoria_mensal_v2.csv')

    def test_preservacao(self):
        self.assertEqual(b.hashfile(b.V1),b.HASH_V1)
        self.assertEqual(len(self.v2),3384);self.assertEqual(len(self.v2[0]),46)
        self.assertEqual(len({(r['codigo_ibge'],r['ano']) for r in self.v2}),3384)
        self.assertEqual(len({r['codigo_ibge'] for r in self.v2}),141)
        for a,c in zip(self.v1,self.v2):self.assertEqual(a,{k:c[k] for k in a})
        # Todos os dez entregáveis publicados da v1 continuam byte a byte iguais.
        root=b.P.parents[5]
        for nome in ['README.md','amostras.csv','construir_base3.py','dicionario_variaveis.csv','manifesto.json','painel_h1_base3_v1.csv','qualidade_variaveis.csv','relatorio_qualidade.md','testar_base3.py','validacao.json']:
            path='2_INTI/chapters/chap1/stats/modelos/base3/'+nome
            blob=subprocess.check_output(['git','show','5c0247fb00248828daa37a49b96e077c0db70bfd:'+path],cwd=b.P)
            self.assertEqual(blob,(b.P/nome).read_bytes(),nome)

    def test_renomeacao_integral_idempotente(self):
        mapa=b.mapa_colunas()
        self.assertEqual(list(self.final[0]),list(mapa.values()))
        self.assertEqual(b.renomear_finais(self.final),self.final)
        self.assertEqual(b.renomear_finais(self.v2),self.final)
        path='2_INTI/chapters/chap1/stats/modelos/base3/painel_h1_base3_v2.csv'
        raw=subprocess.check_output(['git','show','332fc3c3e48acf57695b40bf0b74b0d908e61950:'+path],cwd=b.P)
        before=list(csv.DictReader(io.StringIO(raw.decode())))
        self.assertEqual(self.v2,before)  # Todas as células e ordem, incluindo NA e zeros.
        self.assertEqual((b.P/'painel_h1_base3_v2.csv').read_bytes().split(b'\n',1)[1],raw.split(b'\n',1)[1])
        metadata=b.ler(b.P/'dicionario_variaveis_v2.csv')
        self.assertEqual([r['variavel'] for r in metadata],list(mapa.values()))

    def test_calendario_unidades(self):
        self.assertEqual(len(self.mensal),288)
        self.assertTrue(all(r['selic_4189_pct_aa']!='' for r in self.mensal))
        self.assertTrue(all(all(r[c]!='' for c in b.NOVAS) for r in self.v2))
        self.assertEqual({r['mes'] for r in self.mensal},{f'{y}-{m:02d}' for y in range(2000,2024) for m in range(1,13)})
        self.assertEqual(len({r['ano'] for r in self.anual}),24)
        for a in self.anual:
            self.assertEqual(int(a['ano_referencia']),int(a['ano'])-1)
            rows=[r for r in self.mensal if r['mes'].startswith(a['ano_referencia']+'-')]
            self.assertEqual(len(rows),12)
            for r in rows:
                for c in ['cpi_u','soja_usd_t','milho_usd_t','dap_usd_t','soja_usd2024_t','milho_usd2024_t','dap_usd2024_t']:
                    self.assertTrue(math.isfinite(float(r[c])) and float(r[c])>0)
            dap=statistics.mean(float(r['dap_usd2024_t']) for r in rows)
            self.assertAlmostEqual(float(a[b.NOVAS[0]]),dap,places=10)
            for crop,c in zip(['soja','milho'],b.NOVAS[1:3]):
                expected=statistics.mean(float(r[crop+'_usd2024_t']) for r in rows)/dap
                self.assertAlmostEqual(float(a[c]),expected,places=12)
            rates=[float(r['selic_4189_pct_aa']) for r in rows if r['selic_4189_pct_aa']!='']
            self.assertEqual(int(a['meses_selic']),len(rates))
            self.assertEqual(a['flag_selic_incompleta'],str(len(rates)!=12))
            if len(rates)==12:self.assertAlmostEqual(float(a[b.NOVAS[3]]),statistics.mean(rates),places=12)
            else:self.assertEqual(a[b.NOVAS[3]],'')

    def test_join_many_to_one_e_razoes(self):
        lookup={a['ano']:a for a in self.anual}
        for r in self.v2:
            for c in b.NOVAS:self.assertEqual(r[c],lookup[r['ano']][c])
            for crop,c in zip(['soja','milho'],b.NOVAS[1:3]):
                expected=float(r[f'preco_real_usd2024_media_anual_lag1__{crop}'])/float(r[b.NOVAS[0]])
                self.assertAlmostEqual(float(r[c]),expected,places=12)
        for c in b.NOVAS:
            for y in range(2001,2025):self.assertEqual(len({r[c] for r in self.v2 if int(r['ano'])==y}),1)

    def test_manifesto(self):
        m=json.loads((b.P/'manifesto_v2.json').read_text())
        self.assertEqual(m['mapeamento_sha256'],b.hashfile(b.P/'mapeamento_colunas_v2.csv'))
        self.assertEqual(m['dicionario_sha256'],b.hashfile(b.P/'dicionario_variaveis_v2.csv'))
        self.assertEqual(m['sha256_painel'],b.hashfile(b.P/'painel_h1_base3_v2.csv'))
        self.assertEqual(m['auditoria_previa_sha256'],b.hashfile(b.P/'auditoria_pre_join_v2.json'))
        for name,value in m['fontes'].items():self.assertEqual(value,b.hashfile(b.F/name))

if __name__=='__main__':unittest.main(verbosity=2)
