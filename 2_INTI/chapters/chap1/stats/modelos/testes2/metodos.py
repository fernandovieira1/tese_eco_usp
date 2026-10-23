"""Utilitários auditáveis: FE por projeção, sandwiches, testes e exportação."""
from pathlib import Path
import json, hashlib, time, warnings
import numpy as np
import pandas as pd
from scipy import stats, sparse
from scipy.sparse.csgraph import connected_components
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests

SEMENTE=20261023
MAPA={'codigo_ibge':'id','ano':'ano','bioma_predominante':'bioma','y_nativa_inicial_ha':'estoque','n_autos_flora__ibama_espacial':'autos','flag_contagem_flora_parcial__ibama_espacial':'parcial'}
for produto,alias in [('soja','soja'),('milho','milho'),('carne_bovina','boi')]:MAPA['preco_real_usd2024_media_anual_lag1__'+produto]='p_'+alias
for cultura,codigo in [('soja','soy'),('milho','mze')]:MAPA['capacidade_valor__'+cultura+'__gaez_yxHr0_'+codigo]='a_'+cultura
for uso in ['agricultura','pastagem']:
 MAPA['conversao_ha__'+uso]='ha_'+uso;MAPA['taxa_conversao__'+uso]='taxa_'+uso


def dados(pasta):
    origem=pasta.parent/'painel_municipal_descritiva_h1.csv'
    esperado='bc396a4f394ae60d6883205f2ca6e8d33b59a4fb419fc5d667591374c8f1c730'
    assert hashlib.sha256(origem.read_bytes()).hexdigest()==esperado, 'CSV mudou: requer nova estratégia e revisão das sínteses, não reprodução automática.'
    raw=pd.read_csv(origem,dtype={'codigo_ibge':str})
    d=raw.rename(columns=MAPA).sort_values(['id','ano']).reset_index(drop=True)
    assert d.id.notna().all() and d.id.str.fullmatch(r'\d{7}').all()
    assert d.ano.notna().all() and not d.duplicated(['id','ano']).any()
    flag=d.parcial.astype('string').str.lower()
    assert flag.dropna().isin(['true','false']).all()
    d['autos_validos']=d.autos.where(flag.eq('false') & d.autos.ge(0))
    d['fiscal']=d.groupby('id').autos_validos.shift(1).where(d.ano.eq(d.groupby('id').ano.shift(1)+1))/10
    for u in ['agricultura','pastagem']:
        q=d['taxa_'+u];h=d['ha_'+u];ok=q.notna() & h.notna()
        assert q[ok].between(0,1).all() and h[ok].ge(0).all() and d.estoque[ok].gt(0).all()
        assert np.allclose(q[ok],h[ok]/d.estoque[ok],atol=1e-12)
        d['pp_'+u]=100*q
    escalas=[]
    for c in ['p_soja','p_milho','p_boi','a_soja','a_milho']:
        g='ano' if c.startswith('p_') else 'id'
        assert d.groupby(g)[c].nunique().max()==1
        if c.startswith('p_'):assert d[c].dropna().gt(0).all()
        v=d.drop_duplicates(g)[c];mu=v.mean();sd=v.std(ddof=0)
        d['z_'+c]=(d[c]-mu)/sd;escalas.append(dict(variavel=c,media=mu,dp=sd,base=g))
    for cultura in ['soja','milho']:
        d['expo_'+cultura]=d['z_p_'+cultura]*d['z_a_'+cultura]
        # USD/t dividido por USD/t; todos preços estritamente positivos.
        c='rel_'+cultura;d[c]=np.log(d['p_'+cultura]/(1000*d.p_boi))
        v=d.drop_duplicates('ano')[c];mu=v.mean();sd=v.std(ddof=0)
        d['x_'+c]=(d[c]-mu)/sd*d['z_a_'+cultura]
        escalas.append(dict(variavel=c,media=mu,dp=sd,base='ano'))
    d['preco_fiscal']=d.z_p_soja*d.fiscal
    d['diferenca_pp']=d.pp_pastagem-d.pp_agricultura
    pd.DataFrame(escalas).to_csv(pasta/'escalas.csv',index=False)
    return d


def projetar(s,cols,trend=False,bioma_ano=False):
    """Projeções alternadas em painel desbalanceado; nunca double-demean simples."""
    x=s[cols].astype(float).copy();ids=s.id;tg=(s.bioma.astype(str)+'_'+s.ano.astype(str)) if bioma_ano else s.ano
    t=s.ano-s.groupby('id').ano.transform('mean');den=(t*t).groupby(ids).transform('sum')
    for k in range(2000):
        old=x.to_numpy().copy();x=x-x.groupby(ids).transform('mean')
        if trend:x=x-t.to_numpy()[:,None]*(x.mul(t,axis=0).groupby(ids).transform('sum').div(den.replace(0,np.nan),axis=0).fillna(0))
        x=x-x.groupby(tg).transform('mean')
        if np.max(np.abs(x.to_numpy()-old))<1e-11:break
    else:raise RuntimeError('FE não convergiu')
    gi=pd.factorize(ids)[0];gt=pd.factorize(tg)[0];G=gi.max()+1;H=gt.max()+1
    a=sparse.coo_matrix((np.ones(2*len(s)),(np.r_[gi,G+gt],np.r_[G+gt,gi])),shape=(G+H,G+H)).tocsr()
    comp=connected_components(a,directed=False,return_labels=False);rank_fe=G+H-comp
    if trend:
        fi=pd.get_dummies(ids,dtype=float).to_numpy();ft=pd.get_dummies(tg,dtype=float).to_numpy()
        rank_fe=np.linalg.matrix_rank(np.column_stack([fi,ft,fi*t.to_numpy()[:,None]]))
    return x.to_numpy(),rank_fe,k+1


def covariancias(scores,bread,s,k):
    """HAC temporal dos scores somados; clusters CR1 como sensibilidades."""
    n=len(s);assert n>k
    def meat_group(chave):
        z=pd.DataFrame(scores).groupby(np.asarray(chave)).sum().to_numpy();g=len(z)
        return z.T@z*(g/(g-1))*((n-1)/(n-k))
    z=pd.DataFrame(scores).groupby(s.ano.to_numpy()).sum()
    z=z.reindex(range(int(s.ano.min()),int(s.ano.max())+1),fill_value=0).to_numpy()
    cov={}
    for lag in [1,2,3]:
        meat=z.T@z
        for l in range(1,lag+1):
            gam=z[l:].T@z[:-l];meat+=(1-l/(lag+1))*(gam+gam.T)
        cov['DK'+str(lag)]=bread@meat@bread*n/(n-k)
    cm=meat_group(s.id);ct=meat_group(s.ano)
    # A amostra sempre tem uma observação por município-ano.
    ci=scores.T@scores*n/(n-k)
    cov['municipio']=bread@cm@bread;cov['two_way_bruto']=bread@(cm+ct-ci)@bread
    return {name:(v+v.T)/2 for name,v in cov.items()}


class Experimento:
    def __init__(self,pasta):
        self.p=Path(pasta).resolve();self.d=dados(self.p)
        self.coef=[];self.models=[];self.joint=[];self.sens=[];self.loss=[];self.mag=[]
    def amostra(self,s,cols,ident):
        d=s.copy();n0=len(s)
        for c in cols:
            n=len(d);mask=d[c].notna()
            if pd.api.types.is_numeric_dtype(d[c]):mask &= np.isfinite(d[c])
            d=d.loc[mask].copy();self.loss.append(dict(id=ident,criterio=c,antes=n,excluidos=n-len(d),restantes=len(d),N_candidato=n0))
        assert not d.duplicated(['id','ano']).any()
        return d.reset_index(drop=True)
    def linear(self,ident,y,x,s=None,familia='sensibilidade',trend=False,bioma_ano=False,joint=None,detalhe=True):
        s=self.amostra(self.d if s is None else s,[y,*x,'id','ano'],ident)
        with (self.p/'tentativas.jsonl').open('a') as f:f.write(json.dumps({'id':ident,'status':'iniciado','hora':time.time()})+'\n')
        v,rank_fe,it=projetar(s,[y,*x],trend,bioma_ano);yy=v[:,0];xx=v[:,1:];rank=np.linalg.matrix_rank(xx)
        assert rank==len(x), f'{ident}: regressoras absorvidas/colineares'
        bread=np.linalg.inv(xx.T@xx);b=bread@xx.T@yy;u=yy-xx@b;k=rank_fe+len(x)
        cov=covariancias(xx*u[:,None],bread,s,k)
        meta=dict(id=ident,vd=y,vi=' + '.join(x),estimador='TWFE linear',fe='municipio + '+('bioma×ano' if bioma_ano else 'ano')+(' + tendencias municipais' if trend else ''),N=len(s),N_grade=len(self.d),perdas_grade=len(self.d)-len(s),municipios=s.id.nunique(),anos=s.ano.nunique(),ano_min=s.ano.min(),ano_max=s.ano.max(),K_total=k,rank_regressores=rank,condicao=float(np.linalg.cond(xx)),iteracoes=it,convergiu=True,ajuste=1-float(u@u)/(yy@yy),ajuste_tipo='R2 within',familia=familia,singletons=int(s.groupby('id').size().eq(1).sum()),informativos=int(s.groupby('id').size().gt(1).sum()))
        self.registrar(meta,s,x,b,cov,joint or x,detalhe)
        if detalhe:
            for cultura in ['soja','milho']:
                termo='expo_'+cultura
                if termo in x:
                    q=self.d.drop_duplicates('id')['z_a_'+cultura].quantile([.25,.75]);pv=self.d.drop_duplicates('ano')['p_'+cultura];mult=(q.loc[.75]-q.loc[.25])*.1*pv.mean()/pv.std(ddof=0)
                    self.contraste(ident,'P75-P25 aptidão; +10% preço médio '+cultura,x,b,cov['DK2'],{termo:mult},s,'pp',familia)
        return dict(meta=meta,s=s,x=x,b=b,cov=cov,resid=u,xx=xx,yy=yy,k=k)
    def registrar(self,meta,s,names,b,covs,termos_joint,detalhe=True):
        ident=meta['id'];T=s.ano.nunique();G=s.id.nunique();crit=stats.t.ppf(.975,T-1);cov=covs['DK2'];se=np.sqrt(np.maximum(np.diag(cov),0));pv=2*stats.t.sf(abs(b/se),T-1)
        self.models.append(meta)
        for j,n in enumerate(names):
            self.coef.append({**meta,'termo':n,'coef':b[j],'se':se[j],'ic95_inf':b[j]-crit*se[j],'ic95_sup':b[j]+crit*se[j],'p':pv[j],'df':T-1,'covariancia':'DK Bartlett lag2','classificacao':'imprecisão' if abs(b[j])<=crit*se[j] else ('associação positiva' if b[j]>0 else 'associação negativa'),'limites':'não causal; T curto; GAEZ terras2010; sem equivalência'})
        for nome,v in covs.items():
            diag=np.diag(v);ss=np.sqrt(np.where(diag>=0,diag,np.nan));gl=G-1 if nome=='municipio' else T-1
            for j,n in enumerate(names):self.sens.append(dict(id=ident,termo=n,covariancia=nome,se=ss[j],p=2*stats.t.sf(abs(b[j]/ss[j]),gl),ic95_inf=b[j]-stats.t.ppf(.975,gl)*ss[j],ic95_sup=b[j]+stats.t.ppf(.975,gl)*ss[j],df=gl,min_eigen=float(np.linalg.eigvalsh(v).min())))
        js=[names.index(t) for t in termos_joint];cv=cov[np.ix_(js,js)];vv=b[js];q=len(js)
        ok=np.linalg.matrix_rank(cv)==q and np.linalg.eigvalsh(cv).min()>0
        w=float(vv@np.linalg.solve(cv,vv)/q) if ok else np.nan
        self.joint.append(dict(id=ident,termos=';'.join(termos_joint),F=w,df1=q,df2=T-1,p=stats.f.sf(w,q,T-1),status='estimado' if ok else 'covariancia_singular',familia='conjuntos'))
        if detalhe:
            for nome,v in covs.items():pd.DataFrame(v,index=names,columns=names).to_csv(self.p/f'cov_{ident}_{nome}.csv')
        with (self.p/'tentativas.jsonl').open('a') as f:f.write(json.dumps({'id':ident,'status':'concluido','hora':time.time()})+'\n')
    def contraste(self,ident,nome,names,b,cov,pesos,s,unidade,familia):
        a=np.array([pesos.get(n,0) for n in names]);v=float(a@b);se=np.sqrt(max(0,float(a@cov@a)));crit=stats.t.ppf(.975,s.ano.nunique()-1)
        self.mag.append(dict(id=ident,contraste=nome,estimativa=v,se=se,ic95_inf=v-crit*se,ic95_sup=v+crit*se,p=2*stats.t.sf(abs(v/se),s.ano.nunique()-1),unidade=unidade,familia=familia))
    def glm(self,ident,y,x,s,tipo='PPML',offset=False,familia='sensibilidade'):
        s=self.amostra(s,[y,*x,'estoque','id','ano'],ident)
        formula=y+' ~ '+' + '.join(x)+' + C(id) + C(ano)'
        fam=sm.families.Poisson() if tipo=='PPML' else sm.families.Binomial()
        off=np.log(s.estoque) if offset else None
        with (self.p/'tentativas.jsonl').open('a') as f:f.write(json.dumps({'id':ident,'status':'iniciado','hora':time.time()})+'\n')
        with warnings.catch_warnings(record=True) as ws:
            warnings.simplefilter('always');r=smf.glm(formula,s,family=fam,offset=off).fit(maxiter=200,tol=1e-10)
        assert r.converged and np.isfinite(r.params).all(), 'GLM não convergiu'
        design=r.model.exog;k=np.linalg.matrix_rank(design);assert k==design.shape[1]
        scores=r.model.score_obs(r.params);h=-r.model.hessian(r.params);assert np.linalg.matrix_rank(h)==k
        cvfull=covariancias(scores,np.linalg.inv(h),s,k)
        names=list(r.params.index);ix=[names.index(t) for t in x];b=r.params.to_numpy()[ix];cov={n:v[np.ix_(ix,ix)] for n,v in cvfull.items()}
        pred=r.predict();assert np.isfinite(pred).all()
        meta=dict(id=ident,vd=y,vi=' + '.join(x),estimador=tipo+(' offset estoque' if offset else ''),fe='municipio + ano',N=len(s),N_grade=len(self.d),perdas_grade=len(self.d)-len(s),municipios=s.id.nunique(),anos=s.ano.nunique(),ano_min=s.ano.min(),ano_max=s.ano.max(),K_total=k,rank_regressores=len(x),condicao=float(np.linalg.cond(h)),iteracoes=r.fit_history.get('iteration'),convergiu=r.converged,ajuste=1-r.deviance/r.null_deviance,ajuste_tipo='1-deviance/null',familia=familia,score_max=float(abs(scores.sum(axis=0)).max()),max_abs_coef=float(abs(r.params).max()),pred_min=float(pred.min()),pred_max=float(pred.max()),observacoes_mediana_mun=float(s.groupby('id').size().median()),warnings='; '.join(str(w.message) for w in ws))
        self.registrar(meta,s,x,b,cov,x)
        # Cenário: mantém FE ano, altera somente componente diferencial do preço.
        for cultura in ['soja','milho']:
            termo='expo_'+cultura
            if termo not in x:continue
            pv=self.d.drop_duplicates('ano')['p_'+cultura];delta=.1*pv.mean()/pv.std(ddof=0)
            x1=design.copy();j=names.index(termo);x1[:,j]+=delta*s['z_a_'+cultura].to_numpy()
            eta0=design@r.params.to_numpy()+(off.to_numpy() if offset else 0);eta1=x1@r.params.to_numpy()+(off.to_numpy() if offset else 0)
            if tipo=='PPML':mu0=np.exp(eta0);mu1=np.exp(eta1);dm0=mu0;dm1=mu1
            else:mu0=1/(1+np.exp(-eta0));mu1=1/(1+np.exp(-eta1));dm0=mu0*(1-mu0);dm1=mu1*(1-mu1)
            grad=(dm1[:,None]*x1-dm0[:,None]*design).mean(axis=0);v=float((mu1-mu0).mean());se=np.sqrt(max(0,float(grad@cvfull['DK2']@grad)));crit=stats.t.ppf(.975,s.ano.nunique()-1)
            self.mag.append(dict(id=ident,contraste='+10% preço médio '+cultura+'; só componente diferencial',estimativa=v,se=se,ic95_inf=v-crit*se,ic95_sup=v+crit*se,p=2*stats.t.sf(abs(v/se),s.ano.nunique()-1),unidade='ha' if tipo=='PPML' else 'fração',familia=familia))
        return r
    def salvar(self,classe):
        for nome,rows in [('coef',self.coef),('modelos',self.models),('conjuntos',self.joint),('sensibilidades',self.sens),('perdas',self.loss),('magnitudes',self.mag)]:
            if rows:pd.DataFrame(rows).to_csv(self.p/f'{nome}_{classe}.csv',index=False)


def consolidar(pasta):
    pasta=Path(pasta)
    def combinar(prefixo):
        fs=list(pasta.glob(prefixo+'_*.csv'));d=pd.concat([pd.read_csv(f) for f in fs],ignore_index=True) if fs else pd.DataFrame();return d
    c=combinar('coef');m=combinar('modelos');j=combinar('conjuntos');s=combinar('sensibilidades');l=combinar('perdas');mag=combinar('magnitudes')
    assert not c.duplicated(['id','termo']).any();assert not m.id.duplicated().any()
    assert np.isfinite(c[['coef','se','p']]).all().all()
    for d in [c,j,mag]:
        if d.empty:continue
        d['p_holm']=np.nan;d['n_familia']=0
        for family,g in d.groupby('familia'):
            valid=g.p.notna();ix=g[valid].index
            if len(ix):d.loc[ix,'p_holm']=multipletests(d.loc[ix,'p'],method='holm')[1];d.loc[g.index,'n_familia']=len(ix)
    titulos={'A01':'Núcleo amplo sem autos','A02':'Núcleo na amostra fiscal','A03':'Autuações na amostra comum','A04':'Preço × autuações','A05':'Preços relativos grãos/boi','D01':'Diferença formal entre destinos','G00':'Referência linear harmonizada','Q01':'PPML hectares com FE','Q02':'PPML com offset estoque','F01':'Logit fracional com FE','B01':'Lag1 na amostra de três lags','B02':'Lags distribuídos','B03':'Tendências municipais','B04':'Choques bioma×ano','B05':'Janela 2011–2024','B06':'Primeiras diferenças','D02':'Diferença acumulada entre destinos','D03':'Diferença com tendências','D04':'Diferença com choques bioma×ano','C01':'Dinâmica e tendências','C02':'Dinâmica e choques bioma×ano','C03':'Dinâmica pós2010','I00':'Referência da influência','I':'Exclusão sistemática leave-one-out','H00':'Referência Amazônia/Cerrado','H01':'Slopes distintos por bioma','H02':'Slopes distintos e choques bioma×ano','N01':'Curvatura preço×aptidão','Z01':'Ocorrência agrícola','Z02':'Log taxa agrícola positiva','E01':'Referência com estoque2001 observado','E02':'Intensidade por estoque2001','E03':'Painel fixo de 24 anos','W01':'Inferência do núcleo estático','W02':'Inferência das somas dinâmicas','W03':'Inferência das somas com bioma×ano','W04':'Inferência das somas pós2010'}
    def unidade(y):
        if y.startswith('log_'):return 'log da fração, condicional a taxa positiva'
        if y.startswith('delta_'):return 'diferença anual de pontos percentuais'
        if y.startswith('intensidade2001'):return 'ha por 100ha de estoque2001'
        if y=='ocorrencia_pp':return 'pontos percentuais de ocorrência'
        if y.startswith('ha_'):return 'hectares'
        if y.startswith('taxa_'):return 'fração [0,1]'
        return 'pontos percentuais'
    for dd in [c,m]:
        dd['titulo']=dd.id.str.split('_').str[0].map(titulos)
        dd['unidade_vd']=dd.vd.map(unidade)
        dd['transformacoes']='Preços já lag1; z por ano, aptidão z por município; lags/quadrados/diferenças conforme nomes e estratégia; sem imputação'
        dd['bioma_escopo']=np.where(dd.id.str.startswith('H'),'Amazônia/Cerrado','Todos conforme suporte da amostra')
        dd['periodos_HAC']=dd.anos;dd['clusters_municipio_sensibilidade']=dd.municipios
        inicial=l.groupby('id').N_candidato.first()
        dd['N_apos_pre_filtros']=dd.id.map(inicial)
        dd['perdas_pre_filtros']=dd.N_grade-dd.N_apos_pre_filtros
        dd['perdas_casos_completos']=dd.N_apos_pre_filtros-dd.N
    c['classificacao_ic95_nao_ajustado']=c['classificacao']
    c['interpretacao_multiplicidade']=np.where(c.p_holm.lt(.05),np.where(c.coef.gt(0),'associação positiva após Holm no modelo/família','associação negativa após Holm no modelo/família'),'imprecisão após Holm; não equivale a efeito nulo')
    c['identificacao']='associativa; causalidade de H1 não identificada'
    c['exploratorio_adaptativo']=True
    c['escopo_Holm']='família na rodada; não controla integralmente busca sequencial'
    for name,d in [('COEFICIENTES',c),('MODELOS',m),('TESTES_CONJUNTOS',j),('SENSIBILIDADES',s),('PERDAS',l),('MAGNITUDES',mag)]:d.to_csv(pasta/(name+'.csv'),index=False)
    return c,m,j
