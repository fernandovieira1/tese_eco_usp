"""Recortes literais e seguros por prefixo, parametrizados; padrão congelado base3 v4."""
import argparse,csv,hashlib,io,json
from pathlib import Path
STATS=Path(__file__).resolve().parents[2]
BASE=STATS/'modelos/base3/BASES_PARA_USO'
DESTINO=STATS/'FERNANDO/grupos_h1'
HASH_BASE='a98dbe320efc784543cf43372a5903de32434be5871304178f2f9d49daaf1c3b'
HASH_DIC='8e8a22d3d75742aaa355cfacbbe4d0eb1d16bc14c77fd4459d4db1daa620c4e5'
NOMES={1:'GRUPO_1_AMBIENTAIS.csv',2:'GRUPO_2_ECONOMICOS.csv',3:'GRUPO_3_INSTITUCIONAIS.csv',4:'GRUPO_4_OUTROS.csv'}
def sha(data):return hashlib.sha256(data).hexdigest()
def ler(path):
    with Path(path).open(encoding='utf-8',newline='') as f:
        r=csv.reader(f);return next(r),list(r)
def recortar(origem,dicionario,destino,hash_base,hash_dic):
    origem,dicionario,destino=map(Path,(origem,dicionario,destino))
    assert sha(origem.read_bytes())==hash_base,'Fonte modificada: interrompido'
    assert sha(dicionario.read_bytes())==hash_dic,'Dicionário modificado: interrompido'
    cols,rows=ler(origem);assert len(cols)==len(set(cols))
    assert all(c[:2] in ('0_','1_','2_','3_','4_') for c in cols)
    assert all(len(r)==len(cols) for r in rows)
    indices=[i for i,c in enumerate(cols) if c.startswith('0_')]
    key=[cols.index(c) for c in ('0_codigo_ibge','0_ano')]
    assert len({tuple(r[i] for i in key) for r in rows})==len(rows)
    dc,dr=ler(dicionario);assert [r[dc.index('variavel')] for r in dr]==cols
    payloads={'BASE_COMPLETA_H1.csv':origem.read_bytes(),'DICIONARIO.csv':dicionario.read_bytes()};report={}
    for g,name in NOMES.items():
        chosen=indices+[i for i,c in enumerate(cols) if c.startswith(str(g)+'_')]
        buf=io.StringIO(newline='');writer=csv.writer(buf,lineterminator='\n')
        writer.writerow([cols[i] for i in chosen]);writer.writerows([r[i] for i in chosen] for r in rows)
        payloads[name]=buf.getvalue().encode('utf-8')
        report[name]={'linhas':len(rows),'colunas':len(chosen),'indices':len(indices),'sha256':sha(payloads[name])}
    # Same preflight principle as the v4 separator: validate all outputs before any write.
    for name,data in payloads.items():
        f=destino/name
        if f.exists() and f.read_bytes()!=data:raise RuntimeError(f'Edição manual ou conteúdo divergente: {f}. Preserve o arquivo e use destino vazio.')
    destino.mkdir(parents=True,exist_ok=True)
    for name,data in payloads.items():(destino/name).write_bytes(data)
    return {'fonte_sha256':hash_base,'dicionario_sha256':hash_dic,'linhas':len(rows),'colunas':len(cols),'grupos':report}
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--origem',type=Path,default=BASE/'BASE_COMPLETA_H1.csv');a.add_argument('--dicionario',type=Path,default=BASE/'DICIONARIO.csv');a.add_argument('--destino',type=Path,default=DESTINO);a.add_argument('--hash-base',default=HASH_BASE);a.add_argument('--hash-dicionario',default=HASH_DIC)
    x=a.parse_args();print(json.dumps(recortar(x.origem,x.dicionario,x.destino,x.hash_base,x.hash_dicionario),indent=2))
