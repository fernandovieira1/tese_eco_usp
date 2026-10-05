"""Supplementary event geocoding and auditable MT cost-sheet extraction."""
from data_paths import data_path
import pandas as pd,geopandas as gpd
from data_common import DATA,write_json
from prepare_h1_h2 import save

def main():
    d=pd.read_csv(data_path('processed/tabular/h1__autos_ibama__eventos_MT.csv'),dtype={'codigo_ibge':str,'SEQ_AUTO_INFRACAO':str},low_memory=False)
    x=pd.to_numeric(d.NUM_LONGITUDE_AUTO.astype(str).str.replace(',','.'),errors='coerce')
    y=pd.to_numeric(d.NUM_LATITUDE_AUTO.astype(str).str.replace(',','.'),errors='coerce')
    valid=x.between(-62,-50)&y.between(-19,-7)
    # Datum is a documented working assumption, not authenticated original metadata.
    points=gpd.GeoDataFrame(d.loc[valid,['SEQ_AUTO_INFRACAO','codigo_ibge','ano','valor_multa_nominal']],geometry=gpd.points_from_xy(x[valid],y[valid]),crs=4326)
    m=gpd.read_file('zip://'+str(data_path('raw/vector/ibge/MT_Municipios_2024.zip'))).to_crs(4326)
    joined=gpd.sjoin(points,m[['CD_MUN','geometry']],how='left',predicate='within')
    joined['codigo_ibge_espacial']=joined.CD_MUN
    joined['diverge_codigo_informado']=joined.codigo_ibge_espacial.notna() & (joined.codigo_ibge!=joined.codigo_ibge_espacial)
    result=pd.DataFrame(joined.drop(columns=['geometry','index_right','CD_MUN']))
    save(result,'h1__autos_ibama__geocodificacao_candidata.csv')
    eligible=result[result.codigo_ibge_espacial.notna() & result.SEQ_AUTO_INFRACAO.notna() & ~result.SEQ_AUTO_INFRACAO.duplicated(keep=False) & result.ano.notna()]
    a=eligible.groupby(['codigo_ibge_espacial','ano']).agg(n_autos_ibama_espacial=('SEQ_AUTO_INFRACAO','size'),valor_multas_ibama_espacial=('valor_multa_nominal',lambda s:s.sum(min_count=1))).reset_index().rename(columns={'codigo_ibge_espacial':'codigo_ibge'})
    save(a,'h1__autos_ibama__espacial_municipio_anual_candidato.csv')
    write_json('catalog/ibama_geocodificacao.json',{'n_total':len(d),'n_coordenadas_bbox':int(valid.sum()),'n_sem_poligono':int(result.codigo_ibge_espacial.isna().sum()),'divergencias_codigo':int(result.diverge_codigo_informado.sum()),'assuncao':'coordenadas em graus tratadas provisoriamente como EPSG4326; datum original precisa autenticacao','malha':'IBGE 2024; nao representa historico de limites','zeros_coordenadas':'excluidos da geocodificacao, preservados nos eventos'})
    for p in (data_path('raw/tabular/conab')).glob('*.xls'):
        wb=pd.ExcelFile(p);rows=[];sheets=[]
        for name in wb.sheet_names:
            if '-MT' not in name.upper():continue
            frame=pd.read_excel(wb,sheet_name=name,header=None)
            sheets.append({'aba':name,'linhas':len(frame),'colunas':len(frame.columns)})
            for ri,row in frame.iterrows():
                for ci,val in row.items():
                    if pd.notna(val):rows.append({'arquivo_origem':p.name,'aba':name,'linha_excel':ri+1,'coluna_excel':ci+1,'conteudo':str(val)})
        if rows:save(pd.DataFrame(rows),'h1__costs_conab__'+p.stem+'__MT_celulas.csv')
        write_json('catalog/conab_'+p.stem+'_abas.json',sheets)

if __name__=='__main__':main()
