import csv,io,tempfile,unittest,subprocess
from pathlib import Path
import separar_grupos_h1 as s
class GruposH1(unittest.TestCase):
    def test_publicacao_e_reconstrucao_por_chave(self):
        p=s.BASE/'BASE_COMPLETA_H1.csv';cols,rows=s.ler(p)
        self.assertEqual((len(rows),len(cols)),(3384,97))
        root=s.STATS.parents[3]
        for name in ('BASE_COMPLETA_H1.csv','DICIONARIO.csv'):
            f=s.HISTORICA/name;rel=f.relative_to(root)
            self.assertEqual(f.read_bytes(),subprocess.check_output(['git','show','668b099becfe82ec7fc341ec6b9dc391146a57a5:'+str(rel)],cwd=root))
        original=[dict(zip(cols,r)) for r in rows];key=lambda r:(r['0_codigo_ibge'],r['0_ano'])
        idx=[c for c in cols if c.startswith('0_')];self.assertEqual(len(idx),7)
        rebuilt={key(r):{c:r[c] for c in idx} for r in original};seen=set(idx)
        for g,name in s.NOMES.items():
            cs,rs=s.ler(s.DESTINO/name);self.assertEqual(cs,idx+[c for c in cols if c.startswith(str(g)+'_')]);self.assertEqual(len(rs),3384)
            actual=[dict(zip(cs,r)) for r in rs];self.assertEqual([key(r) for r in actual],[key(r) for r in original]);self.assertEqual(len({key(r) for r in actual}),3384)
            for a,b in zip(original,actual):self.assertEqual(b,{c:a[c] for c in cs});rebuilt[key(b)].update(b)
            specific=set(cs)-set(idx);self.assertFalse(specific&seen);seen|=specific
        self.assertEqual(seen,set(cols))
        buf=io.StringIO(newline='');w=csv.writer(buf,lineterminator='\n');w.writerow(cols);w.writerows([rebuilt[key(r)][c] for c in cols] for r in original)
        self.assertEqual(buf.getvalue().encode(),p.read_bytes())
    def test_dicionario_e_pasta(self):
        self.assertEqual((s.DESTINO/'DICIONARIO.csv').read_bytes(),(s.BASE/'DICIONARIO.csv').read_bytes())
        self.assertEqual({f.name for f in s.DESTINO.iterdir()},set(s.NOMES.values())|{'BASE_COMPLETA_H1.csv','DICIONARIO.csv','LEIA_ME.md'})
    def test_reproducao_duas_vezes_e_edicao_manual(self):
        for _ in range(2):
            with tempfile.TemporaryDirectory() as tmp:
                dest=Path(tmp);args=(s.BASE/'BASE_COMPLETA_H1.csv',s.BASE/'DICIONARIO.csv',dest,s.HASH_BASE,s.HASH_DIC)
                s.recortar(*args)
                for f in dest.iterdir():self.assertEqual(f.read_bytes(),(s.DESTINO/f.name).read_bytes())
                edited=dest/s.NOMES[1];edited.write_bytes(edited.read_bytes()+b'EDICAO\n');before={f.name:f.read_bytes() for f in dest.iterdir()}
                with self.assertRaises(RuntimeError):s.recortar(*args)
                self.assertEqual(before,{f.name:f.read_bytes() for f in dest.iterdir()})
if __name__=='__main__':unittest.main(verbosity=2)
