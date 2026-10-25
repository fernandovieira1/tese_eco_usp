import tempfile,unittest
from pathlib import Path
import incorporar_custos_h1 as s
class Incorporacao(unittest.TestCase):
    def test_duas_reproducoes_preservacao_recomposicao(self):
        resultados=[]
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                dest=Path(tmp); report=s.incorporar(s.HISTORICA,dest)
                self.assertEqual((report['linhas'],report['colunas'],report['custos']),(3384,97,27))
                oldc,oldr=s.ler(s.HISTORICA/'BASE_COMPLETA_H1.csv'); c,r=s.ler(dest/'BASE_COMPLETA_H1.csv')
                self.assertEqual(c[:70],oldc);self.assertEqual([{k:x[k] for k in oldc} for x in r],oldr)
                fc,fr=s.ler(s.FONTE);fm=s.mapa(fr)
                for x in r:self.assertEqual({k:x[k] for k in fc},fm[s.chave(x)])
                rebuilt={s.chave(x):{} for x in r}
                for g,name in enumerate(s.GRUPOS,1):
                    gc,gr=s.ler(dest/name)
                    self.assertEqual([s.chave(x) for x in gr],[s.chave(x) for x in r])
                    for x in gr:rebuilt[s.chave(x)].update(x)
                    if g!=2:self.assertEqual((dest/name).read_bytes(),(s.HISTORICA/name).read_bytes())
                self.assertEqual([rebuilt[s.chave(x)] for x in r],r)
                _,dr=s.ler(dest/'DICIONARIO.csv');self.assertEqual([x['variavel'] for x in dr],c)
                snapshot={p.name:p.read_bytes() for p in dest.iterdir()}
                self.assertEqual(s.incorporar(dest,dest)['adicionadas'],0)
                self.assertEqual(snapshot,{p.name:p.read_bytes() for p in dest.iterdir()});resultados.append(snapshot)
        self.assertEqual(*resultados)
    def test_ativa_igual_reproducao(self):
        payload,_=s.preparar(s.HISTORICA)
        for name,data in payload.items():self.assertEqual((s.ATIVA/name).read_bytes(),data)
    def test_colisao_custo_nao_escreve(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);s.incorporar(s.HISTORICA,d)
            for name in ('BASE_COMPLETA_H1.csv',s.GRUPOS[1]):
                c,r=s.ler(d/name);v=next(k for k in c if k.startswith('2_custo_'));r[0][v]='123456';(d/name).write_bytes(s.serializar(c,r))
            before={p.name:p.read_bytes() for p in d.iterdir()}
            with self.assertRaisesRegex(ValueError,'Colisão'):s.incorporar(d,d)
            self.assertEqual(before,{p.name:p.read_bytes() for p in d.iterdir()})
    def test_edicao_manual_coerente_preservada(self):
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp)
            for p in s.HISTORICA.iterdir():(d/p.name).write_bytes(p.read_bytes())
            for name in ('BASE_COMPLETA_H1.csv',s.GRUPOS[1]):
                c,r=s.ler(d/name);v=next(k for k in c if k.startswith('2_'));r[0][v]='EDICAO_MANUAL';(d/name).write_bytes(s.serializar(c,r))
            s.incorporar(d,d);self.assertEqual(s.ler(d/'BASE_COMPLETA_H1.csv')[1][0][v],'EDICAO_MANUAL')
    def test_chaves_e_indices_invalidos(self):
        for modo in ('duplicada','indice'):
            with tempfile.TemporaryDirectory() as tmp:
                d=Path(tmp)
                for p in s.HISTORICA.iterdir():(d/p.name).write_bytes(p.read_bytes())
                c,r=s.ler(d/'BASE_COMPLETA_H1.csv')
                if modo=='duplicada':r[1]=dict(r[0])
                else:r[0][next(k for k in c if k.startswith('0_') and k not in s.CHAVE)]='DIVERGENTE'
                (d/'BASE_COMPLETA_H1.csv').write_bytes(s.serializar(c,r))
                before={p.name:p.read_bytes() for p in d.iterdir()}
                with self.assertRaises(ValueError):s.incorporar(d,d)
                self.assertEqual(before,{p.name:p.read_bytes() for p in d.iterdir()})
if __name__=='__main__':unittest.main(verbosity=2)
