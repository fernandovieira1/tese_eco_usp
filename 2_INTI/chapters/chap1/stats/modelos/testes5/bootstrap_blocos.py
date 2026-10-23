"""Wild restrito por blocos calendários; enumeração não garante exatidão inferencial."""
import itertools,json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats
from metodos import projetar,covariancias

def wild_restrito(r,pesos,nome,bloco=3,bioma_ano=False,pasta=None):
    s=r['s'];x=r['xx'];y=r['yy'];b=r['b'];n=len(s);k=r['k'];names=r['x']
    a=np.array([pesos.get(t,0.) for t in names]);bread=np.linalg.inv(x.T@x)
    # Mínimos quadrados sob a'β=0, mantendo os demais slopes livres.
    b0=b-bread@a*(a@b)/(a@bread@a);assert abs(a@b0)<1e-10
    u0=y-x@b0;gr=((s.ano-s.ano.min())//bloco).to_numpy(dtype=int);G=int(gr.max()+1)
    assert G<=14  # Enumeração limitada e definida pelo suporte, não p.
    signs=np.array(list(itertools.product([-1.,1.],repeat=G))).T
    B=signs.shape[1];base=np.zeros((n,G));base[np.arange(n),gr]=u0
    tmp=s.copy();cn=[f'_resid_bloco_{j}' for j in range(G)]
    for j,col in enumerate(cn):tmp[col]=base[:,j]
    v,rank,it=projetar(tmp,cn,bioma_ano=bioma_ano)
    incremento=bread@x.T@v;ubase=v-x@incremento
    scorebase=pd.DataFrame(ubase*(x@bread@a)[:,None]).groupby(s.ano.to_numpy()).sum()
    scorebase=scorebase.reindex(range(int(s.ano.min()),int(s.ano.max())+1),fill_value=0).to_numpy()
    z=scorebase@signs
    variancia=(z*z).sum(axis=0)
    for lag in [1,2]:variancia+=2*(1-lag/3)*(z[lag:]*z[:-lag]).sum(axis=0)
    variancia*=n/(n-k)
    numerador=float(a@b0)+(a@incremento)@signs
    valido=variancia>1e-24;tstar=np.full(B,np.nan);tstar[valido]=numerador[valido]/np.sqrt(variancia[valido])
    se=np.sqrt(float(a@r['cov']['DK2']@a));tobs=float(a@b)/se
    assert np.isclose(tstar[-1],tobs,rtol=1e-7,atol=1e-8)
    # Dois padrões conferidos contra a reestimação direta com FE.
    for q in [0,B//3]:
        tmp['_y_boot']=s[r['meta']['vd']].to_numpy()-u0+u0*signs[gr,q]
        vv,rf,_=projetar(tmp,['_y_boot',*names],bioma_ano=bioma_ano)
        bb=np.linalg.solve(vv[:,1:].T@vv[:,1:],vv[:,1:].T@vv[:,0]);uu=vv[:,0]-vv[:,1:]@bb
        cc=covariancias(vv[:,1:]*uu[:,None],bread,s,k)['DK2'];td=(a@bb)/np.sqrt(a@cc@a)
        assert np.isclose(td,tstar[q],rtol=1e-6,atol=1e-7)
    extremos=int(np.sum(np.abs(tstar[valido])>=abs(tobs)-1e-10));falhas=int((~valido).sum());pw=extremos/B if falhas==0 else np.nan
    crit=stats.t.ppf(.975,s.ano.nunique()-1)
    ident=r['meta']['id'];f=Path(pasta)/f'bootstrap_{ident}_{nome}_b{bloco}.csv.gz'
    pd.DataFrame({'padrao':np.arange(B),'sinais_binarios':[format(i,f'0{G}b') for i in range(B)],'t_boot':tstar,'variancia_contraste':variancia}).to_csv(f,index=False,compression='gzip')
    return dict(id=ident,contraste=nome,vd=r['meta']['vd'],estimativa=float(a@b),se_DK2=se,ic95_DK_inf=float(a@b)-crit*se,ic95_DK_sup=float(a@b)+crit*se,p_DK2=2*stats.t.sf(abs(tobs),s.ano.nunique()-1),bloco_anos=bloco,blocos=G,padroes=B,t_observado=tobs,p_wild=pw,p_limite_inferior=extremos/B,p_limite_superior=(extremos+falhas)/B,variancias_degeneradas=falhas,N=n,municipios=s.id.nunique(),anos=s.ano.nunique(),null_restricao=float(a@b0),reestimacao_direta_verificada=True,limites='independência/simetria dos blocos não verificadas; IC é DK, não bootstrap')
