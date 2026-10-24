"""Integridade dos recortes e proteção das edições manuais."""
import csv,io,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import separar_grupos_v4 as s
class Grupos(unittest.TestCase):
    def test_particao_indices_ordem_e_reconstrucao(self):
        cols,rows=s.ler(s.PAINEL);index=[c for c in cols if c.startswith('0_')]
        original=[dict(zip(cols,r)) for r in rows];keys=lambda r:(r['0_codigo_ibge'],r['0_ano'])
        rebuilt={keys(r):{c:r[c] for c in index} for r in original};seen=set(index)
        for group,name in s.NOMES.items():
            cs,rs=s.ler(s.USO/name);expected=index+[c for c in cols if c.startswith(str(group)+'_')]
            self.assertEqual(cs,expected);self.assertEqual(len(rs),3384)
            actual=[dict(zip(cs,r)) for r in rs];self.assertEqual([keys(r) for r in actual],[keys(r) for r in original]);self.assertEqual(len({keys(r) for r in actual}),3384)
            for before,after in zip(original,actual):
                self.assertEqual({c:before[c] for c in index},{c:after[c] for c in index})
                self.assertEqual(after,{c:before[c] for c in cs})
                rebuilt[keys(after)].update(after)
            new=set(cs)-set(index);self.assertFalse(new & seen);seen|=new
        self.assertEqual(seen,set(cols))
        reconstructed=[[rebuilt[keys(r)][c] for c in cols] for r in original]
        self.assertEqual(reconstructed,rows)
        buf=io.StringIO(newline='');w=csv.writer(buf,lineterminator='\n');w.writerow(cols);w.writerows(reconstructed)
        self.assertEqual(buf.getvalue().encode(),s.PAINEL.read_bytes())
    def test_manifesto_dicionario_e_sete_arquivos(self):
        m=json.loads((s.P/'manifesto_grupos_v4.json').read_text())
        for name,info in m['arquivos'].items():self.assertEqual(s.sha((s.USO/name).read_bytes()),info['sha256'])
        cols,rows=s.ler(s.DIC);self.assertEqual([r[cols.index('variavel')] for r in rows],s.ler(s.PAINEL)[0])
        self.assertEqual({f.name for f in s.USO.iterdir()},set(m['arquivos'])|{'LEIA_ME.md'})
    def test_duas_reproducoes_e_recusa_edicoes(self):
        for _ in range(2):
            with tempfile.TemporaryDirectory() as d:
                root=Path(d);s.separar(root)
                for name in s.NOMES.values():self.assertEqual((root/name).read_bytes(),(s.USO/name).read_bytes())
                changed=root/s.NOMES[2];changed.write_bytes(changed.read_bytes()+b'EDICAO_MANUAL\n')
                before={f.name:f.read_bytes() for f in root.iterdir()}
                with self.assertRaises(RuntimeError):s.separar(root)
                self.assertEqual(before,{f.name:f.read_bytes() for f in root.iterdir()})
                # The builder calls the same guard before any reconstruction output.
                (root/'manifesto_grupos_v4.json').write_bytes((s.P/'manifesto_grupos_v4.json').read_bytes())
                with patch.object(s,'P',root),patch.object(s,'USO',root):
                    with self.assertRaises(RuntimeError):s.verificar_publicados()
if __name__=='__main__':unittest.main(verbosity=2)
