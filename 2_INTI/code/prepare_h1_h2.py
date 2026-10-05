"""Transparent candidate tables. No regression, imputation or territorial backcasting.

Numeric missing values retain the original SIDRA symbol in companion columns.
MapBiomas native vegetation is an explicit candidate taxonomic definition.
"""
from data_paths import data_path
import json, re, unicodedata, zipfile
import pandas as pd
import numpy as np
import openpyxl
from data_common import DATA, write_json
from data_paths import sync_shared

def save(df,name):
    relative='processed/tabular/'+name
    target=data_path(relative)
    target.parent.mkdir(parents=True,exist_ok=True)
    df.to_csv(target,index=False,encoding='utf-8-sig')
    sync_shared(relative,replace=True)
    print(name,len(df),flush=True)

def norm(s):
    return ''.join(c for c in unicodedata.normalize('NFKD',str(s).upper()) if not unicodedata.combining(c)).replace("'",'').strip()

def sidra():
    names={'109':'area_plantada_ha','216':'area_colhida_ha','214':'producao_t','112':'rendimento_medio_kg_ha','105':'efetivo_bovino'}
    for table,label in [('1612','pam_soja_milho'),('3939','ppm_bovinos')]:
        rows=[]
        for p in sorted((data_path('raw/tabular/ibge')).glob(f't{table}_*.json')):
            a=json.loads(p.read_text(encoding='utf-8'))
            for v in a:
                for result in v['resultados']:
                    product=next(iter(result['classificacoes'][0]['categoria'].values()))
                    for s in result['series']:
                        for year,raw in s['serie'].items():
                            rows.append({'codigo_ibge':s['localidade']['id'],'municipio':s['localidade']['nome'].removesuffix(' - MT'),'uf':'MT','ano':int(year),'produto':product,'variavel':names[v['id']],'valor_original':raw})
        d=pd.DataFrame(rows)
        assert not d.duplicated(['codigo_ibge','ano','produto','variavel']).any()
        d['valor']=pd.to_numeric(d.valor_original,errors='coerce')
        keys=['codigo_ibge','municipio','uf','ano','produto']
        w=d.pivot(index=keys,columns='variavel',values='valor')
        flags=d.pivot(index=keys,columns='variavel',values='valor_original').add_suffix('__original')
        w=w.join(flags).reset_index()
        if table=='1612':
            w['yield_calculado_kg_ha']=w.producao_t*1000/w.area_colhida_ha.where(w.area_colhida_ha>0)
            w['yield_diferenca_kg_ha']=w.yield_calculado_kg_ha-w.rendimento_medio_kg_ha
            w['yield_soja_kg_ha_it']=w.rendimento_medio_kg_ha.where(w.produto=='Soja (em grão)')
        save(w,f'h1_h2__{label}__ibge__municipio_anual.csv')

def mapbiomas():
    p=data_path('raw/tabular/mapbiomas/collection10_1_coverage.xlsx')
    wb=openpyxl.load_workbook(p,read_only=True,data_only=True)
    it=wb['COVERAGE_10.1'].iter_rows(values_only=True); header=next(it)[:51]
    rows=[r[:51] for r in it if r[3]=='MT']
    d=pd.DataFrame(rows,columns=header)
    lookup=json.loads((data_path('raw/tabular/ibge/municipios_mt_consulta20260928.json')).read_text(encoding='utf-8'))
    lookup={norm(r['nome']):str(r['id']) for r in lookup}
    d['codigo_ibge']=d.municipality.map(lambda x:lookup.get(norm(x)))
    unmatched=d[d.codigo_ibge.isna()].copy()
    save(unmatched,'mapbiomas_col10_1__MT_sem_correspondencia_IBGE__quarentena.csv')
    d=d[d.codigo_ibge.notna()].copy()
    assert not d.duplicated(['codigo_ibge','biome','class_id']).any()
    # Source's row classes are leaves; exclude bare rock/apicum/water from native vegetation.
    native=[3,4,5,6,49,11,12,50]
    l=d.melt(id_vars=['codigo_ibge','municipality','biome','class_id'],value_vars=list(range(1985,2025)),var_name='ano',value_name='area_ha')
    l.ano=l.ano.astype(int)
    save(l,'h1_h2__mapbiomas_classes__col10_1__municipio_bioma_anual.csv')
    keys=['codigo_ibge','municipality','ano']
    totals=l.groupby(keys).area_ha.sum(min_count=1).rename('area_mapeada_ha')
    nat=l[l.class_id.isin(native)].groupby(keys).area_ha.sum(min_count=1).rename('native_veg_ha_it')
    w=totals.to_frame().join(nat).reset_index().rename(columns={'municipality':'municipio'})
    w['uf']='MT';w['native_veg_share_it']=w.native_veg_ha_it/w.area_mapeada_ha
    w=w.sort_values(['codigo_ibge','ano'])
    for col in ['native_veg_ha_it','native_veg_share_it']:
        w[col.replace('_it','_lag1')]=w.groupby('codigo_ibge')[col].shift(1).where(w.groupby('codigo_ibge').ano.diff()==1)
    save(w,'h2__native_veg__mapbiomas_col10_1__candidato.csv')
    legend=[r[:5] for r in wb['LEGEND_CODE'].iter_rows(min_row=4,max_row=60,values_only=True) if any(x is not None for x in r[:5])]
    write_json('catalog/mapbiomas_legenda_taxonomia.json',{'classes_nativas_candidatas':native,'excluidas_da_vegetacao':[29,32,33,31],'denominador':'soma de todas as classes mapeadas; inclui agua e nao observado','legend_rows':legend,'crosswalk':'nome normalizado exato + UF; cadastro IBGE 2026; nao constitui harmonizacao historica'})

def prices():
    w=openpyxl.load_workbook(data_path('raw/tabular/worldbank/pink_sheet_monthly_20260930.xlsx'),read_only=True,data_only=True)
    rows=list(w['Monthly Prices'].values); h=rows[4];units=rows[5]
    cols=[(h.index('Soybeans'),'price_soja'),(h.index('Maize'),'price_milho'),(h.index('Beef **'),'price_carne_bovina')]
    result=[]
    for r in rows[6:]:
        if not isinstance(r[0],str) or not re.fullmatch(r'\d{4}M\d{2}',r[0]):continue
        for i,name in cols:
            result.append({'data':r[0].replace('M','-')+'-01','variavel':name,'valor_original':r[i],'unidade':units[i],'moeda':'USD','mercado':'internacional; ver Description no XLSX','deflator':'nenhum'})
    d=pd.DataFrame(result); d['preco_nominal']=pd.to_numeric(d.valor_original,errors='coerce')
    d=d.sort_values(['variavel','data']); d['ln_price']=np.log(d.preco_nominal.where(d.preco_nominal>0))
    d['dln_price']=d.groupby('variavel').ln_price.diff()
    save(d,'h1__prices__worldbank__mensal_robustez.csv')

def vectors():
    import geopandas as gpd
    m=gpd.read_file('zip://'+str(data_path('raw/vector/ibge/MT_Municipios_2024.zip')))
    b=gpd.read_file('zip://'+str(data_path('raw/vector/ibge/Biomas_250mil_2019.zip')))
    print('VECTOR SCHEMA',list(m.columns),list(b.columns),flush=True)
    info={}
    for name,g in [('municipios_2024',m),('biomas_2019',b)]:
        info[name]={'n':len(g),'crs':str(g.crs),'bbox':g.total_bounds.tolist(),'invalidas':int((~g.is_valid).sum()),'schema':list(g.columns)}
    write_json('catalog/validacao_vetores.json',info)
    # Equal-area CRS for shares, not geographic degree areas.
    mm=m.to_crs('EPSG:5880');bb=b.to_crs('EPSG:5880')
    repair=[]
    for label,g in [('municipios',mm),('biomas',bb)]:
        bad=~g.is_valid
        for idx in g.index[bad]:
            old=g.at[idx,'geometry'];new=old.make_valid() if hasattr(old,'make_valid') else __import__('shapely').make_valid(old)
            repair.append({'dataset':label,'index':int(idx),'area_before_m2':old.area,'area_after_m2':new.area,'method':'shapely.make_valid after EPSG:5880 projection'})
            g.at[idx,'geometry']=new
    write_json('catalog/reparo_geometria_projecao.json',repair)
    assert mm.is_valid.all() and bb.is_valid.all()
    namecol=next(c for c in b.columns if 'bioma' in c.lower())
    inter=gpd.overlay(mm[['CD_MUN','NM_MUN','geometry']],bb[[namecol,'geometry']],how='intersection',keep_geom_type=True)
    inter['area_m2']=inter.area
    area=mm.set_index('CD_MUN').area
    tab=inter.groupby(['CD_MUN',namecol]).area_m2.sum().unstack(fill_value=0).div(area,axis=0)
    out=pd.DataFrame({'codigo_ibge':mm.CD_MUN,'municipio':mm.NM_MUN}).set_index('codigo_ibge')
    for col,target in [('Amazônia','amazonia'),('Cerrado','cerrado'),('Pantanal','pantanal')]:
        out['biome_'+target+'_share_i']=tab[col]
    shares=out.filter(like='_share_i');out['soma_fracoes']=shares.sum(axis=1)
    for pct in [70,80,90]:
        out[f'biome_class_{pct}']=shares.idxmax(axis=1).str.replace('biome_','').str.replace('_share_i','').where(shares.max(axis=1)>=pct/100,'misto')
    save(out.reset_index(),'h2__biome_share__ibge2019_malha2024__candidato.csv')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--stage',choices=['sidra','mapbiomas','prices','vectors'],required=True)
    globals()[p.parse_args().stage]()
