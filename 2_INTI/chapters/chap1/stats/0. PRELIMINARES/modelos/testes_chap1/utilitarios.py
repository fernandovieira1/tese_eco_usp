"""Leitura explícita, estimação e exportação; fórmulas ficam nos notebooks."""
from pathlib import Path
import json, hashlib, platform, warnings
import numpy as np
import pandas as pd
import scipy.stats as st
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups, cov_cluster
from linearmodels.panel import PanelOLS

PASTA = Path(__file__).resolve().parent
RAIZ = next(p for p in PASTA.parents if (p / 'AGENTS.md').exists())
CSV = PASTA.parent / 'painel_municipal_descritiva_h1.csv'
AUDIT = RAIZ / '2_INTI/audit/testes_chap1_20261023'
SEMENTE = 20261023
MAPA = {'codigo_ibge':'id', 'ano':'ano', 'bioma_predominante':'bioma',
 'y_nativa_inicial_ha':'estoque', 'n_autos_flora__ibama_espacial':'autos',
 'flag_contagem_flora_parcial__ibama_espacial':'parcial',
 'preco_real_usd2024_media_anual_lag1__soja':'p_soja',
 'preco_real_usd2024_media_anual_lag1__milho':'p_milho',
 'preco_real_usd2024_media_anual_lag1__carne_bovina':'p_boi',
 'capacidade_valor__soja__gaez_yxHr0_soy':'a_soja',
 'capacidade_valor__milho__gaez_yxHr0_mze':'a_milho'}
for uso in ['agricultura','pastagem']:
 MAPA['conversao_ha__'+uso] = 'ha_'+uso
 MAPA['taxa_conversao__'+uso] = 'taxa_'+uso


def ler():
    """Sem imputação; mantém taxas zero e exclui somente valores inválidos."""
    raw = pd.read_csv(CSV, dtype={'codigo_ibge':str})
    assert set(MAPA).issubset(raw.columns)
    d = raw.rename(columns=MAPA).sort_values(['id','ano']).copy()
    assert not d.duplicated(['id','ano']).any()
    assert d.id.str.fullmatch(r'\d{7}').all()
    assert d.ano.notna().all() and np.equal(d.ano,d.ano.astype(int)).all()
    d['parcial'] = d.parcial.astype('string').str.lower().map({'true':True,'false':False})
    # Ausência/contagem parcial não equivale a zero autos.
    d['autos_validos'] = d.autos.where(d.parcial.eq(False) & d.autos.ge(0))
    anterior = d.groupby('id').ano.shift(1)
    d['fiscal'] = d.groupby('id').autos_validos.shift(1).where(d.ano.eq(anterior+1)) / 10
    for u in ['agricultura','pastagem']:
        q=d['taxa_'+u];h=d['ha_'+u]
        valido = d.estoque.gt(0) & h.ge(0) & q.between(0,1)
        assert np.allclose((h/d.estoque)[valido],q[valido],atol=1e-12)
        d['taxa_'+u]=q.where(valido)
        d['ha_'+u]=h.where(valido)
        d['pp_'+u]=100*d['taxa_'+u]  # Taxa em pontos percentuais.
    escalas=[]
    for c in ['p_soja','p_milho','p_boi','a_soja','a_milho']:
        grupo='ano' if c.startswith('p_') else 'id'
        assert d.groupby(grupo)[c].nunique().max() == 1
        v=d.drop_duplicates(grupo)[c]; media=v.mean();dp=v.std(ddof=0)
        assert dp>0
        d['z_'+c]=(d[c]-media)/dp
        escalas.append({'variavel':c,'media':media,'dp':dp,'base':grupo})
    # Produto padronizado é exposição, não receita comercial por hectare.
    d['expo_soja']=d.z_p_soja*d.z_a_soja
    d['expo_milho']=d.z_p_milho*d.z_a_milho
    d['preco_fiscal']=d.z_p_soja*d.fiscal
    pd.DataFrame(escalas).to_csv(PASTA/'escalas.csv',index=False)
    return d


def amostra(d, colunas, modelo):
    """Perdas sequenciais em ordem declarada, sem duplicar exclusões."""
    s=d.copy(); perdas=[]
    for c in colunas:
        n=len(s); s=s.loc[s[c].notna() & (~np.isinf(s[c]) if pd.api.types.is_numeric_dtype(s[c]) else True)]
        perdas.append({'id_modelo':modelo,'criterio':c,'antes':n,'excluidos':n-len(s),'restantes':len(s)})
    pd.DataFrame(perdas).to_csv(PASTA/f'perdas_{modelo}.csv',index=False)
    return s


def estimar(formula,s,estimador='OLS',fe='nenhum'):
    """Retorna ajuste e covariâncias; não decide especificações."""
    if estimador=='PainelOLS':
        r=PanelOLS.from_formula(formula,s.set_index(['id','ano']),drop_absorbed=False,check_rank=True).fit(cov_type='clustered',cluster_entity=True,cluster_time=True,debiased=True)
        return r, np.asarray(r.cov), None
    if estimador in ['PPML','Fracional']:
        familia=sm.families.Poisson() if estimador=='PPML' else sm.families.Binomial()
        r=smf.glm(formula,s,family=familia).fit(maxiter=200,tol=1e-9)
        assert r.converged, 'GLM não convergiu'
    else:r=smf.ols(formula,s).fit()
    grupos=np.column_stack([pd.factorize(s.id)[0],pd.factorize(s.ano)[0]])
    cov,cm,ct=cov_cluster_2groups(r,grupos,use_correction=True)
    return r,cov,cm


def cov_psd(cov):
    """Projeção espectral explícita: autovalores negativos viram zero."""
    valores, vetores=np.linalg.eigh((cov+cov.T)/2)
    return (vetores*np.maximum(valores,0))@vetores.T


def exportar(ident,titulo,formula,s,r,cov,estimador,fe,vd,base_n=3384,cm=None,alerta=''):
    """Tabela longa inclui termos de FE; t usa o menor número de clusters menos um."""
    painel=estimador=='PainelOLS';its=estimador=='ITS'
    b=r.params; nomes=list(b.index); k=len(b)
    pd.DataFrame(cov,index=nomes,columns=nomes).to_csv(PASTA/f'cov_bruta_{ident}.csv')
    g=s.id.nunique() if 'id' in s else int(s.n_municipios.iloc[0]);t=s.ano.nunique()
    gl=(len(s)-k) if its else min(g,t)-1
    crit=st.t.ppf(.975,gl)
    diag_raw=np.diag(cov);se_raw=np.sqrt(np.where(diag_raw>=0,diag_raw,np.nan))
    eig=np.linalg.eigvalsh(cov);neg=bool(eig.min() < -1e-10)
    if neg:cov=cov_psd(cov)
    diag=np.diag(cov);se=np.sqrt(np.maximum(diag,0))
    p=2*st.t.sf(np.abs(np.asarray(b)/se),gl)
    if painel:ajuste=float(r.rsquared);tipo='R2 transformado FE';rank=k;cond=np.nan
    else:
        x=r.model.exog;rank=int(np.linalg.matrix_rank(x));cond=float(np.linalg.cond(x))
        if estimador in ['PPML','Fracional']:ajuste=1-r.deviance/r.null_deviance;tipo='1-deviance/null_deviance'
        else:ajuste=float(r.rsquared);tipo='R2'
    assert rank==k, 'Matriz de desenho sem posto completo'
    alertas=alerta+'; associação sem identificação causal; poucos anos para inferência'
    if neg:alertas+='; two-way bruto não PSD: projeção espectral aplicada, bruto preservado; sensibilidade relevante'
    if np.any(diag_raw<0):alertas+='; SE bruto ausente para variância bruta negativa'
    if not its:alertas+='; dependência espacial entre municípios não resolvida'
    registros=[]
    for j,nome in enumerate(nomes):
        registros.append(dict(id=ident,titulo=titulo,vd=vd,vi=formula,transformacoes='preços lag1 e aptidão em z; fiscalização lag1 por 10 autos; taxa em pp exceto fracional',estimador=estimador,fe=fe,anos=f'{s.ano.min()}–{s.ano.max()}',amostra='casos completos; sem imputação' if not its else 'agregado da amostra fixa',bioma='todos; predominância municipal',N_inicial=base_n,N=len(s),perdas=base_n-len(s),municipios=g,clusters_municipio=g if not its else 0,clusters_ano=t if not its else 0,df_inferencia=gl,termo=nome,coef=float(b.iloc[j]),se=se[j],se_two_way_bruto=se_raw[j],cov_correcao='PSD espectral' if neg else 'nenhuma',ic95_inf=b.iloc[j]-crit*se[j],ic95_sup=b.iloc[j]+crit*se[j],p=p[j],ajuste_tipo=tipo,ajuste=ajuste,posto=rank,condicao=cond,convergiu=getattr(r,'converged',True),cov_min_eigen=float(eig.min()),alertas=alertas,interpretacao='Coeficiente condicional; IC que inclui zero é compatível com associação nula.'))
    out=pd.DataFrame(registros)
    escala='log média de hectares' if estimador=='PPML' else ('log-odds da taxa' if estimador=='Fracional' else 'pontos percentuais')
    out['interpretacao']=[f'Associação de {v:+.4g} {escala} por unidade do termo; IC inclui zero.' if lo<=0<=hi else f'Associação de {v:+.4g} {escala} por unidade do termo; IC exclui zero, sem interpretação causal.' for v,lo,hi in zip(out.coef,out.ic95_inf,out.ic95_sup)]
    out.to_csv(PASTA/f'coef_{ident}.csv',index=False)
    residuos=np.asarray(r.resids if painel else r.resid_response if estimador in ['PPML','Fracional'] else r.resid)
    basico={'id':ident,'resid_media':float(residuos.mean()),'resid_dp':float(residuos.std()),'municipios_singleton':int(s.groupby('id').size().eq(1).sum()) if 'id' in s else 0,'coef_max_abs':float(np.abs(b).max()),'cov_correcao':'PSD espectral' if neg else 'nenhuma'}
    pd.DataFrame([basico]).to_csv(PASTA/f'diagnostico_base_{ident}.csv',index=False)
    if cm is not None:
        se1=np.sqrt(np.maximum(np.diag(cm),0));pd.DataFrame({'id':ident,'termo':nomes,'se_cluster_municipio':se1}).to_csv(PASTA/f'sensibilidade_{ident}.csv',index=False)
    return out.loc[~out.termo.str.contains('C\(',regex=True),['id','termo','coef','se','ic95_inf','ic95_sup','p','N','alertas']].head(14)


def marginais(r,cov,s,ident,tipo):
    """AME de preço z via preço × aptidão, com delta method e t conservador."""
    b=np.asarray(r.params);x=r.model.exog;nomes=list(r.params.index);out=[]
    if np.linalg.eigvalsh(cov).min() < -1e-10:cov=cov_psd(cov)
    for cultura in ['soja','milho']:
        j=nomes.index('expo_'+cultura);apt=s['z_a_'+cultura].to_numpy()
        def efeito(v):
            eta=x@v
            if tipo=='Fracional':
                mu=1/(1+np.exp(-eta));der=mu*(1-mu)
            else:der=np.exp(eta)
            return np.mean(der*v[j]*apt)
        grad=np.array([(efeito(b+np.eye(len(b))[i]*1e-5)-efeito(b-np.eye(len(b))[i]*1e-5))/2e-5 for i in range(len(b))])
        var=grad@cov@grad;se=np.sqrt(var) if var>=0 else np.nan;crit=st.t.ppf(.975,min(s.id.nunique(),s.ano.nunique())-1);v=efeito(b)
        out.append({'id':ident,'preco':cultura,'ame':v,'se':se,'ic95_inf':v-crit*se,'ic95_sup':v+crit*se,'unidade':'fração por 1 DP preço' if tipo=='Fracional' else 'ha por 1 DP preço','limite':'componente diferencial preço×aptidão; efeito comum anual não identificado'})
    pd.DataFrame(out).to_csv(PASTA/f'marginais_{ident}.csv',index=False)
    return pd.DataFrame(out)
