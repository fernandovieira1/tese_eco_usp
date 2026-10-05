"""Event-preserving IBAMA extraction. Reported municipality is not spatial proof.

Keep cancellations/statuses; count registered events without implying exogeneity.
Personal identifiers are retained only in the original source archives.
"""
from data_paths import data_path
import zipfile
import pandas as pd
from data_common import DATA,write_json
from prepare_h1_h2 import save

def main():
    rows=[]; audit=[]
    cols=['SEQ_AUTO_INFRACAO','NUM_AUTO_INFRACAO','SER_AUTO_INFRACAO','VAL_AUTO_INFRACAO','DAT_HORA_AUTO_INFRACAO','DT_FATO_INFRACIONAL','COD_MUNICIPIO','MUNICIPIO','UF','TIPO_INFRACAO','DES_INFRACAO','SIT_CANCELADO','DS_SIT_AUTO_AIE','QT_AREA','INFRACAO_AREA','NUM_LONGITUDE_AUTO','NUM_LATITUDE_AUTO','DS_WKT','DS_ENQUADRAMENTO_ADMINISTRATIVO','ULTIMA_ATUALIZACAO_RELATORIO']
    with zipfile.ZipFile(data_path('raw/tabular/ibama/auto_infracao_csv.zip')) as z:
        assert z.testzip() is None
        for name in z.namelist():
            d=pd.read_csv(z.open(name),sep=';',dtype=str,encoding='utf-8',usecols=lambda c:c in cols,keep_default_na=False)
            mt=d[d.UF=='MT'].copy();mt['arquivo_origem']=name
            rows.append(mt);audit.append({'arquivo':name,'n_brasil':len(d),'n_mt':len(mt)})
    d=pd.concat(rows,ignore_index=True)
    d['codigo_ibge']=d.COD_MUNICIPIO
    d['ano']=pd.to_datetime(d.DAT_HORA_AUTO_INFRACAO,errors='coerce',format='mixed').dt.year.astype('Int64')
    d['valor_multa_nominal']=pd.to_numeric(d.VAL_AUTO_INFRACAO.str.replace('.','',regex=False).str.replace(',','.',regex=False),errors='coerce')
    d['flag_codigo_mt']=d.codigo_ibge.str.fullmatch(r'51\d{5}')
    d['flag_id_duplicado']=d.SEQ_AUTO_INFRACAO.duplicated(keep=False)
    d['flag_id_ausente']=d.SEQ_AUTO_INFRACAO.eq('')
    save(d,'h1__autos_ibama__eventos_MT.csv')
    eligible=d[d.flag_codigo_mt & d.ano.notna() & ~d.flag_id_duplicado]
    g=eligible.groupby(['codigo_ibge','ano'])
    annual=g.agg(n_autos_ibama_it=('SEQ_AUTO_INFRACAO','size'),n_valores_ausentes=('valor_multa_nominal',lambda s:int(s.isna().sum()))).join(g.valor_multa_nominal.sum(min_count=1).rename('valor_multas_ibama_it')).reset_index()
    save(annual,'h1__autos_multas_ibama__municipio_anual_candidato.csv')
    write_json('catalog/ibama_validacao_eventos.json',{'particoes':audit,'n_mt':len(d),'ids_ausentes':int(d.flag_id_ausente.sum()),'ids_duplicados_nao_vazios':int((d.flag_id_duplicado & ~d.flag_id_ausente).sum()),'codigo_invalido':int((~d.flag_codigo_mt).sum()),'data_invalida':int(d.ano.isna().sum()),'valores_ausentes':int(d.valor_multa_nominal.isna().sum()),'regra':'data da lavratura ISO com ou sem horario; todos status; sem preencher municipio-ano ausente com zero; geocodificacao candidata separada; area sem unidade confirmada nao somada'})

if __name__=='__main__':main()
