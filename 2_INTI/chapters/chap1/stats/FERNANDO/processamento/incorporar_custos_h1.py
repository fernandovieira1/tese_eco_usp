"""Incorporação aprovada de 27 custos; junção textual 1:1, sem reestimar valores.
Para reprodução limpa: --base modelos/base3/BASES_PARA_USO --destino DIRETORIO_VAZIO.
O padrão atualiza o conjunto ativo apenas após validar todos os arquivos.
"""
import argparse, csv, hashlib, io, json
from pathlib import Path
STATS = Path(__file__).resolve().parents[2]
ATIVA = STATS/'FERNANDO/grupos_h1'
HISTORICA = STATS/'modelos/base3/BASES_PARA_USO'
PARALELA = STATS/'modelos/base_custos_investigacao/etapa_regional_v2'
FONTE = PARALELA/'USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv'
DIC_FONTE = PARALELA/'USO_CANDIDATOS/DICIONARIO.csv'
HASH_FONTE = '083d3ead60fd30f70a87673fc6265cc23e2fc2383d2fb13bf5832dfc8be39a4b'
HASH_DIC_FONTE = '05ed5af69e3cd176000a002615f0abdc9a42791619a2ff7677f83e06ba16ad7d'
GRUPOS = ['GRUPO_1_AMBIENTAIS.csv','GRUPO_2_ECONOMICOS.csv','GRUPO_3_INSTITUCIONAIS.csv','GRUPO_4_OUTROS.csv']
CHAVE = ['0_codigo_ibge','0_ano']
def sha(b): return hashlib.sha256(b).hexdigest()
def ler(p):
    with Path(p).open(encoding='utf-8',newline='') as f:
        r=csv.DictReader(f); cols=r.fieldnames; rows=list(r)
    if len(cols)!=len(set(cols)) or any(None in r or None in r.values() for r in rows):
        raise ValueError(f'CSV inválido: {p}')
    return cols,rows
def serializar(cols,rows):
    s=io.StringIO(newline=''); w=csv.DictWriter(s,fieldnames=cols,lineterminator='\n',extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    return s.getvalue().encode('utf-8')
def chave(r): return tuple(r[c] for c in CHAVE)
def mapa(rows):
    m={chave(r):r for r in rows}
    if len(m)!=len(rows): raise ValueError('Chaves duplicadas')
    return m

def preparar(base,fonte=FONTE,dic_fonte=DIC_FONTE):
    base=Path(base)
    if sha(Path(fonte).read_bytes())!=HASH_FONTE or sha(Path(dic_fonte).read_bytes())!=HASH_DIC_FONTE:
        raise ValueError('Snapshot de custos divergente do aprovado')
    cols,rows=ler(base/'BASE_COMPLETA_H1.csv'); original=mapa(rows)
    fc,fr=ler(fonte); fm=mapa(fr); idx=[c for c in cols if c.startswith('0_')]
    custos=[c for c in fc if not c.startswith('0_')]
    if len(rows)!=3384 or len(idx)!=7 or len(custos)!=27 or not all(c.startswith('2_') for c in custos):
        raise ValueError('Dimensões ou prefixos inesperados')
    if [c for c in fc if c.startswith('0_')]!=idx or original.keys()!=fm.keys(): raise ValueError('Suporte/chaves incompatíveis')
    for r in rows:
        if any(r[c]!=fm[chave(r)][c] for c in idx): raise ValueError(f'Índice divergente: {chave(r)}')
    # Certificar recomposição antes da incorporação, inclusive edições manuais coerentes.
    vistos=set(idx); payload={}
    for g,nome in enumerate(GRUPOS,1):
        gc,gr=ler(base/nome); mapa(gr)
        esperado=idx+[c for c in cols if c.startswith(f'{g}_')]
        if gc!=esperado or len(gr)!=len(rows): raise ValueError(f'Colunas/linhas incompatíveis: {nome}')
        for a,b in zip(rows,gr):
            if any(a[c]!=b[c] for c in gc): raise ValueError(f'Grupo divergente: {nome}, {chave(a)}')
        if vistos.intersection(set(gc)-set(idx)): raise ValueError('Sobreposição entre grupos')
        vistos.update(gc); payload[nome]=(base/nome).read_bytes()
    if vistos!=set(cols): raise ValueError('Campos sem grupo')
    for c in custos:
        if c in cols and any(r[c]!=fm[chave(r)][c] for r in rows): raise ValueError(f'Colisão de custo: {c}')
    novos=[c for c in custos if c not in cols]
    saida=[dict(r,**{c:fm[chave(r)][c] for c in novos}) for r in rows]
    outcols=cols+novos
    dc,dr=ler(base/'DICIONARIO.csv')
    if [r['variavel'] for r in dr]!=cols: raise ValueError('Dicionário incompatível')
    _,df=ler(dic_fonte); dm={r['variavel']:r for r in df}
    for c in novos:
        d=dm[c]; row={k:'' for k in dc}
        row.update(posicao=str(len(dr)+1),grupo='2',nome_anterior=c,nome_novo=c,variavel=c,
          justificativa='Incorporação das 27 colunas autorizada pelo autor em 25/10/2026.',papel='custo aproximado',
          definicao=f"{d['atividade']}; sistema {d['sistema']}; conceito {d['conceito']}; moeda {d['moeda']}; ano: {d['ano']}.",
          unidade=d['unidade'],fonte=f"{d['fonte']}; snapshot publicado 72c3e6b531881762b821547015cb916ecc3951c9",campo_origem=c,
          transformacao='Cópia textual por município e ano. Referência regional; na ausência, estadual publicada compatível; nenhuma interpolação.',
          limitacoes='Aproximação, não custo observado municipal. Uma praça: suporte fraco. Conceitos/sistemas/moedas distintos; NA não é zero. Não comprova disponibilidade ex ante. Metadados: ../../modelos/base_custos_investigacao/etapa_regional_v2/resultados/METADADOS_CUSTOS_MUNICIPAIS.csv. O indicador de aprovação desse snapshot descreve a etapa anterior à incorporação.')
        dr.append(row)
    payload['BASE_COMPLETA_H1.csv']=serializar(outcols,saida)
    payload[GRUPOS[1]]=serializar(idx+[c for c in outcols if c.startswith('2_')],saida)
    payload['DICIONARIO.csv']=serializar(dc,dr)
    payload['LEIA_ME.md']=('''# Base H1 para uso

Abra **BASE_COMPLETA_H1.csv**: 3.384 linhas (141 unidades × 2001–2024), 97 colunas. Base v4 com receitas e 27 custos incorporados mediante aprovação do autor em 25/10/2026.

Os quatro grupos repetem os mesmos sete índices: ambientais 29 colunas; econômicos 67; institucionais 12; outros 10. A união por `0_codigo_ibge` e `0_ano`, deduplicando os índices, recompõe a base completa. Consulte DICIONARIO.csv para as 97 variáveis.

Custos são aproximações regionais ou estaduais publicadas compatíveis, não observações municipais independentes. As 27 colunas são alternativas por fonte/conceito/sistema/moeda. Agricultura mantém R$/ha e USD2024/ha separados; pecuária mantém R$/arroba vendida nominal. Ausência permanece vazia, não zero; não houve interpolação. Uma praça significa suporte fraco. Uso econométrico requer considerar informação regional compartilhada e disponibilidade temporal, sem interpretação causal automática.

[Proveniência e qualidade por chave/variável](../../modelos/base_custos_investigacao/etapa_regional_v2/resultados/METADADOS_CUSTOS_MUNICIPAIS.csv). O campo de aprovação desse snapshot refere-se à etapa candidata anterior; a incorporação atual está autorizada. [Fonte literal dos 27 custos](../../modelos/base_custos_investigacao/etapa_regional_v2/USO_CANDIDATOS/CUSTOS_MUNICIPAIS_CANDIDATOS.csv), commit 72c3e6b531881762b821547015cb916ecc3951c9.

Histórico v4 sem custos preservado em `../../modelos/base3/BASES_PARA_USO`. Construção: `../processamento/incorporar_custos_h1.py`; separação: `../processamento/separar_grupos_h1.py`. Para reproduzir, use diretório vazio. Edições manuais coerentes da base e do respectivo grupo são preservadas; colisões diferentes nos custos interrompem a incorporação. A separação recusa sobrescrever arquivos divergentes. Guarde suas edições antes de executar rotinas.
''').encode('utf-8')
    if not novos:
        payload['LEIA_ME.md']=(base/'LEIA_ME.md').read_bytes()
    return payload,{'linhas':len(rows),'colunas':len(outcols),'custos':len(custos),'adicionadas':len(novos),'fonte_sha256':HASH_FONTE,'nao_ausentes':{c:sum(r[c]!='' for r in saida) for c in custos},'sha256':{n:sha(b) for n,b in payload.items()}}

def incorporar(base=ATIVA,destino=ATIVA):
    base,destino=Path(base),Path(destino)
    # Snapshot otimista: não sobrescrever uma edição concorrente.
    antes={p.name:p.read_bytes() for p in base.iterdir() if p.is_file()}
    payload,report=preparar(base)
    for n,b in payload.items():
        p=destino/n
        if p.exists() and p.read_bytes()!=b:
            if destino.resolve()!=base.resolve() or p.read_bytes()!=antes.get(n):
                raise RuntimeError(f'Destino divergente: {p}')
    if any((base/n).read_bytes()!=b for n,b in antes.items()): raise RuntimeError('Edição concorrente detectada')
    destino.mkdir(parents=True,exist_ok=True)
    for n,b in payload.items():
        if not (destino/n).exists() or (destino/n).read_bytes()!=b: (destino/n).write_bytes(b)
    return report
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--base',type=Path,default=ATIVA);a.add_argument('--destino',type=Path,default=ATIVA);x=a.parse_args()
    print(json.dumps(incorporar(x.base,x.destino),ensure_ascii=False,indent=2))
