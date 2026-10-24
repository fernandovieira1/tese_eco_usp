"""Recortes literais da v4 congelada; não infere tipos nem sobrescreve edições."""
import csv
import hashlib
import io
import json
from pathlib import Path
P=Path(__file__).resolve().parent
USO=P/'BASES_PARA_USO'
PAINEL=USO/'BASE_COMPLETA_H1.csv'
DIC=USO/'DICIONARIO.csv'
HASH='a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b'
NOMES={1:'GRUPO_1_AMBIENTAIS.csv',2:'GRUPO_2_ECONOMICOS.csv',3:'GRUPO_3_INSTITUCIONAIS.csv',4:'GRUPO_4_OUTROS.csv'}
def sha(data):return hashlib.sha256(data).hexdigest()
def ler(path):
    with path.open(encoding='utf-8',newline='') as f:
        reader=csv.reader(f);return next(reader),list(reader)
def verificar_publicados():
    manifest=P/'manifesto_grupos_v4.json'
    if manifest.exists():
        for name,info in json.loads(manifest.read_text())['arquivos'].items():
            f=USO/name
            if f.exists() and sha(f.read_bytes())!=info['sha256']:
                raise RuntimeError(f'Edição manual detectada em {f}; preserve sua cópia e reconstrua em checkout separado.')
def separar(destino=USO):
    verificar_publicados()
    assert sha(PAINEL.read_bytes())==HASH,'Base completa difere da v4 publicada'
    columns,rows=ler(PAINEL)
    assert len(columns)==len(set(columns))==70 and len(rows)==3384
    assert all(c[:2] in ('0_','1_','2_','3_','4_') for c in columns)
    assert all(len(r)==70 for r in rows)
    keys=[columns.index(c) for c in ('0_codigo_ibge','0_ano')]
    assert len({tuple(r[i] for i in keys) for r in rows})==3384
    indices=[i for i,c in enumerate(columns) if c.startswith('0_')]
    assert len(indices)==7
    payloads={};infos={}
    for g,name in NOMES.items():
        chosen=indices+[i for i,c in enumerate(columns) if c.startswith(str(g)+'_')]
        buf=io.StringIO(newline='');w=csv.writer(buf,lineterminator='\n')
        w.writerow([columns[i] for i in chosen]);w.writerows([r[i] for i in chosen] for r in rows)
        data=buf.getvalue().encode('utf-8');payloads[name]=data
        infos[name]={'linhas':len(rows),'colunas':len(chosen),'grupo0':7,'variaveis_grupo':len(chosen)-7,'sha256':sha(data)}
    destino=Path(destino)
    # Preflight every output before writing any: never overwrite manual edits.
    for name,data in payloads.items():
        f=destino/name
        if f.exists() and f.read_bytes()!=data:raise RuntimeError(f'Conteúdo diferente em {f}; preserve a edição manual. Use destino vazio.')
    destino.mkdir(parents=True,exist_ok=True)
    for name,data in payloads.items():(destino/name).write_bytes(data)
    infos['BASE_COMPLETA_H1.csv']={'linhas':3384,'colunas':70,'sha256':HASH}
    infos['DICIONARIO.csv']={'linhas':70,'sha256':sha(DIC.read_bytes())}
    if destino.resolve()==USO.resolve():
        (P/'manifesto_grupos_v4.json').write_text(json.dumps({'origem':'base3 v4 publicada; nomes e valores inalterados','chave':['0_codigo_ibge','0_ano'],'grupo0':[columns[i] for i in indices],'arquivos':infos,'na_preservado':True,'sem_inferencia_tipos':True},ensure_ascii=False,indent=2)+'\n')
    return infos
if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('--destino',type=Path,default=USO)
    print(json.dumps(separar(a.parse_args().destino),ensure_ascii=False,indent=2))
