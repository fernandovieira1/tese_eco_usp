"""Somente preparação e contrastes; estimador comum auditável em ../testes2/metodos.py."""
import json,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

def preparar(d):
    d=d.copy()
    for c in ['soja','milho']:
        # Preço já defasado; log válido pois estritamente positivo.
        v=np.log(d['p_'+c]);d['lp_'+c]=v-v.groupby(d.ano).first().mean()
        d['x_'+c]=d['lp_'+c]*d['z_a_'+c]
    return d

def auditar(d,s,r,p):
    shares=list(d.filter(like='biome_'));m=d.drop_duplicates('id');rows=[]
    for nome,a in [('grade',d),('completa',s),('sem_Pantanal',r)]:
        for bi,g in a.groupby('bioma'):
            rows.append(dict(amostra=nome,grupo=bi,N=len(g),municipios=g.id.nunique(),informativos=g.groupby('id').size().gt(1).sum(),anos=g.ano.nunique(),ano_min=g.ano.min(),ano_max=g.ano.max()))
        for t in [1e-6,.05,.1]:
            h=a[shares].gt(t).sum(axis=1).gt(1)
            for val in [False,True]:
                g=a.loc[h.eq(val)];rows.append(dict(amostra=nome,grupo=f'misto_{t}_{val}',N=len(g),municipios=g.id.nunique(),informativos=g.groupby('id').size().gt(1).sum(),anos=g.ano.nunique(),ano_min=g.ano.min(),ano_max=g.ano.max()))
    out=pd.DataFrame(rows);out.to_csv(p/'SUPORTE.csv',index=False)
    for t in [1e-6,.05,.1]:
        h=r[shares].gt(t).sum(axis=1).gt(1)
        assert all(r.loc[h.eq(v)].groupby('id').size().gt(1).sum()>=20 for v in [True,False]),'Suporte insuficiente; parar interface.'
    r.groupby(['bioma','ano']).agg(N=('id','size'),municipios=('id','nunique')).to_csv(p/'SUPORTE_ANUAL.csv')
    m[['id','bioma',*shares]].to_csv(p/'FRACOES_MUNICIPAIS.csv',index=False)
    prices=d.drop_duplicates('ano')[['lp_soja','lp_milho']];prices.corr().to_csv(p/'CORRELACAO_PRECOS.csv')
    m[['z_a_soja','z_a_milho']].corr().to_csv(p/'CORRELACAO_APTIDOES.csv')
    aux=p.parent.parent/'EDA/paineis/painel_tese_chap1_pt.csv';header=pd.read_csv(aux,nrows=0)
    raw=pd.read_csv(p.parent/'painel_municipal_descritiva_h1.csv',nrows=0)
    inventory=[]
    for name,cols in [('painel_exato',raw.columns),('EDA_apenas_inventario',header.columns)]:
        inventory.extend(dict(fonte=name,coluna=c,cultura='soja' if 'soja' in c else ('milho' if 'milho' in c else 'outra')) for c in cols)
    pd.DataFrame(inventory).to_csv(p/'INVENTARIO_COLUNAS.csv',index=False)
    meta={'linhas':len(d),'colunas_origem':len(raw.columns),'municipios':d.id.nunique(),'duplicatas':int(d.duplicated(['id','ano']).sum()),'sha256_csv':hashlib.sha256((p.parent/'painel_municipal_descritiva_h1.csv').read_bytes()).hexdigest(),'sha256_aux_apenas_inventario':hashlib.sha256(aux.read_bytes()).hexdigest(),'algodao_colunas':[c for c in header if 'algod' in c.lower() or 'cotton' in c.lower()],'fracao_soma_erro_max':float(abs(m[shares].sum(axis=1)-1).max()),'fracao_faltantes':int(d[shares].isna().sum().sum()),'fracao_invariante':bool(d.groupby('id')[shares].nunique().max().eq(1).all()),'fracao_min':float(m[shares].min().min()),'fracao_max':float(m[shares].max().max()),'conversao_cultura_disponivel':False,'geometria_json_municipios':False,'arquivos_geograficos_stats':[str(f.relative_to(p.parent.parent)) for f in p.parent.parent.rglob('*') if f.suffix.lower() in ['.gpkg','.shp','.geojson']]}
    (p/'AUDITORIA.json').write_text(json.dumps(meta,indent=2,ensure_ascii=False));print(meta);return out

def ajustar(e,ident,y,s,h=None,familia='culturas',bio=False):
    s=s.copy();x=['x_soja','x_milho'];joint=x.copy()
    if h is not None:
        for c in ['soja','milho']:
            s['xh_'+c]=s['x_'+c]*s[h];s['ph_'+c]=s['lp_'+c]*s[h]
        x += ['xh_soja','xh_milho'];joint=['xh_soja','xh_milho']
        if not bio:x += ['ph_soja','ph_milho']
    fit=e.linear(ident,y,x,s=s,familia=familia,bioma_ano=bio,joint=joint)
    contrasts={'Soja menos milho; gradiente base':{'x_soja':1,'x_milho':-1}}
    if h is not None:
        contrasts.update({'Incremento territorial soja':{'xh_soja':1},'Incremento territorial milho':{'xh_milho':1},'Diferença dos incrementos soja menos milho':{'xh_soja':1,'xh_milho':-1}})
    for nome,w in contrasts.items():
        e.contraste(ident,nome,x,fit['b'],fit['cov']['DK2'],w,fit['s'],'pp por log-preço × DP aptidão','contrastes_formais')
        # Mesmo contraste com cada sandwich; não seleciona covariância pelo p.
        records=[]
        for cov,v in fit['cov'].items():
            a=np.array([w.get(n,0) for n in x]);variance=float(a@v@a);se=np.sqrt(variance) if variance>=0 else np.nan;est=float(a@fit['b']);df=fit['s'].id.nunique()-1 if cov=='municipio' else fit['s'].ano.nunique()-1
            records.append(dict(id=ident,contraste=nome,covariancia=cov,estimativa=est,se=se,p=2*stats.t.sf(abs(est/se),df),ic95_inf=est-stats.t.ppf(.975,df)*se,ic95_sup=est+stats.t.ppf(.975,df)*se,df=df))
        file=e.p/'CONTRASTES_SENSIBILIDADE.csv';pd.DataFrame(records).to_csv(file,mode='a',header=not file.exists(),index=False)
    for c in ['soja','milho']:
        q=e.d.drop_duplicates('id')['z_a_'+c].quantile([.25,.75]);w={'x_'+c:np.log(1.1)*(q.loc[.75]-q.loc[.25])}
        e.contraste(ident,'+10% preço '+c+'; aptidão P75−P25; grupo base',x,fit['b'],fit['cov']['DK2'],w,fit['s'],'pp','magnitudes_base')
    return fit
