"""Robustez preço × aptidão: 4 candidatas e 4 bases, TWFE e amostra comum.
Cluster municipal versus cluster município+ano. Sem modificar o dashboard.
"""
from pathlib import Path
import os,sys,json,hashlib,subprocess,datetime,traceback
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent;APP=HERE.parent
sys.path.insert(0,str(APP))
import numpy as np
import pandas as pd
import statsmodels
from scipy import stats
from h1lab.data import load_data,ROOT,CSV,DICIO,sha256,KEYS
from h1lab.models import fit_model,prepare_sample
from h1lab.ui import pretty
IDS=['M022','M042','M072','M092','M122','M142','M172','M192']
FOCUS=['M042','M092','M142','M192']
BASE={'M042':'M022','M092':'M072','M142':'M122','M192':'M172'}
FILTERS={'years':[2001,2024],'biomes':['Amazônia','Cerrado','Pantanal'],'municipalities':[]}
def clean(x):
    if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)):return [clean(v) for v in x]
    if isinstance(x,np.generic):x=x.item()
    if isinstance(x,float) and not np.isfinite(x):return None
    return x
def save(name,x):(HERE/name).write_text(json.dumps(clean(x),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf8')
def sid(d):return hashlib.sha256(d[KEYS].sort_values(KEYS).to_csv(index=False).encode()).hexdigest()
def effects(d):return pd.concat([pd.DataFrame({'const':np.ones(len(d))}),*[pd.get_dummies(d[k].astype('string'),prefix='FE_'+k,drop_first=True,dtype=float) for k in KEYS]],axis=1)
def sandwich(pinv,resid,codes,K):
    codes=np.asarray(codes);unique,inv=np.unique(codes,return_inverse=True)
    scores=np.zeros((len(unique),K));np.add.at(scores,inv,pinv.T*resid[:,None])
    N=len(resid);G=len(unique)
    return scores.T@scores*(G/(G-1))*((N-1)/(N-K))
def run():
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='main'
    full,cat,data=load_data()
    allold=json.loads((APP/'execucao_fe_candidatas/resultados_fe.json').read_text(encoding='utf8'))
    old={r['plan']['id']:r for r in allold if r['plan']['id'] in IDS}
    assert len(old)==8
    previous_files=[APP/'RESULTADOS_DASH_H1.xlsx',APP/'RESULTADOS_DASH_H1_FE.xlsx',*APP.glob('RESULTADOS_DASH_H1_backup_*.xlsx')]
    sources={p.name:sha256(p) for p in previous_files}
    code={str(p.relative_to(ROOT)):sha256(p) for p in [APP/'h1lab/models.py',APP/'h1lab/data.py',APP/'app.py']}
    samples={mid:prepare_sample(full,FILTERS,old[mid]['plan']['original_spec'])[0] for mid in IDS}
    common=set.intersection(*[set(map(tuple,d[KEYS].values.tolist())) for d in samples.values()])
    common_df=full.loc[[tuple(v) in common for v in full[KEYS].values.tolist()],KEYS+['municipio','bioma_dominante']].copy()
    common_df.to_csv(HERE/'amostra_comum.csv',index=False)
    plan={'created':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
       'focus':FOCUS,'reference_without_interaction':BASE,'ids':IDS,'covariances':['cluster_entity','cluster_twoway'],
       'filters':FILTERS,'common_N':len(common),'common_sample_sha256':sid(common_df),'source_xlsx_sha256':sources,
       'csv_sha256':data['csv_sha256'],'code_sha256':code,
       'criterion':'Sem nova escolha de proxy, amostra, transformação ou termo por resultado. Interseção dos casos completos das 8 especificações originais antes de retirar termos absorvidos. 16 ajustes TWFE: 8 matrizes por duas covariâncias. Sem bootstrap ou novas famílias.'}
    plan_path=HERE/'plano_robustez.json'
    if plan_path.exists():
        existing=json.loads(plan_path.read_text(encoding='utf8'))
        assert all(existing[k]==v for k,v in plan.items() if k!='created'),'Fontes/plano mudaram; requer diretório de execução novo.'
        plan=existing
    else:save(plan_path.name,plan)
    records=[];failures=[]
    for mid in IDS:
        original=old[mid];spec=original['plan']['original_spec']
        # Keep all years for exact calendar lags, masking only this Y outside common keys.
        masked=full.copy();masked.loc[[tuple(v) not in common for v in full[KEYS].values.tolist()],spec['y']]=np.nan
        d,terms,ledger,missing,scales=prepare_sample(masked,FILTERS,spec)
        assert len(d)==len(common) and sid(d)==sid(common_df)
        F=effects(d).to_numpy(float);x=d[terms].to_numpy(float)
        rx=x-F@np.linalg.lstsq(F,x,rcond=None)[0]
        ratios=np.linalg.norm(rx,axis=0)/np.maximum(np.linalg.norm(x,axis=0),np.finfo(float).tiny)
        keep=[t for t,r in zip(terms,ratios) if r>1e-10]
        absorbed=[t for t,r in zip(terms,ratios) if r<=1e-10]
        assert absorbed==original['absorbed'] and keep==original['kept']
        assert len(absorbed)==3
        d[KEYS+[spec['y'],*terms]].to_csv(HERE/(mid+'_amostra_transformada.csv'),index=False)
        pair=[]
        for cov in plan['covariances']:
            rid=mid+('_MUN' if cov=='cluster_entity' else '_MUN_ANO');path=HERE/(rid+'.json')
            if path.exists():
                record=json.loads(path.read_text(encoding='utf8'))
                assert record['sample_id']==sid(common_df) and record['source_fingerprint']==hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest()
                pair.append(record);records.append(record);continue
            try:
                reduced={'y':spec['y'],'xs':keep,'fe':'twoway','cov':cov,'require_y':True,'transforms':{},'lags':{},'interactions':[]}
                model=fit_model(d,FILTERS,reduced);s=model['summary'];X=model['design'].to_numpy(float);K=X.shape[1]
                assert sid(model['sample'])==sid(common_df) and s['N']==len(common)
                rawcov=np.asarray(model['fit'].cov_params());diag=np.diag(rawcov)
                ix=[model['design'].columns.get_loc(t) for t in keep]
                eco=rawcov[np.ix_(ix,ix)];sc=np.sqrt(np.maximum(np.abs(np.diag(eco)),np.finfo(float).tiny))
                scaled_eig=np.linalg.eigvalsh((eco/np.outer(sc,sc)+(eco/np.outer(sc,sc)).T)/2)
                full_eigs=np.linalg.eigvalsh((rawcov+rawcov.T)/2)
                allcoef=model['all_coefficients'].reset_index()
                allcoef['variance']=diag
                allcoef['inference_status']=['Indisponível: variância negativa na covariância cluster; coeficiente pontual mantido.' if v<0 else 'Indisponível: EP/estatística/IC não finito.' if not np.isfinite(se) or se<=0 else 'Marginal calculável; covariância global pode ser indefinida.' for v,se in zip(diag,allcoef['se'])]
                # Independent two-way covariance, with inclusion-exclusion and finite corrections.
                pinv=np.linalg.pinv(X);u=model['diagnostics'].residuo.to_numpy(float)
                entity=pd.factorize(d.codigo_ibge,sort=True)[0];year=pd.factorize(d.ano,sort=True)[0]
                v_entity=sandwich(pinv,u,entity,K)
                if cov=='cluster_twoway':
                    v_year=sandwich(pinv,u,year,K)
                    v_pair=sandwich(pinv,u,np.arange(len(d)),K) # unique municipality-year keys
                    independent=v_entity+v_year-v_pair
                else:independent=v_entity
                np.testing.assert_allclose(independent,rawcov,rtol=1e-7,atol=1e-9)
                maxerr=float(np.max(np.abs(independent-rawcov)))
                if cov=='cluster_twoway':assert s['Graus de liberdade da inferência']==min(s['Municípios'],s['Anos'])-1
                yy=d[spec['y']].to_numpy(float);ry=yy-F@np.linalg.lstsq(F,yy,rcond=None)[0]
                xr=d[keep].to_numpy(float);xr=xr-F@np.linalg.lstsq(F,xr,rcond=None)[0]
                beta=np.linalg.lstsq(xr,ry,rcond=None)[0]
                np.testing.assert_allclose(beta,model['coefficients'].loc[keep,'coef'],rtol=1e-7,atol=1e-8)
                if sid(d)==original['sample_id']:
                    previous={v['term']:v['coef'] for v in original['fits']['TWFE município + ano']['coef']}
                    np.testing.assert_allclose([previous[t] for t in keep],model['coefficients'].loc[keep,'coef'],rtol=1e-10,atol=1e-10)
                record={'id':rid,'candidate':mid,'y':spec['y'],'original_spec':spec,'fit_spec':reduced,'summary':s,
                  'sample_id':sid(d),'sample_min':int(d.ano.min()),'sample_max':int(d.ano.max()),
                  'per_year':d.groupby('ano').size().to_dict(),'per_biome':d.groupby('bioma_dominante').size().to_dict(),
                  'original_sample_N':len(samples[mid]),'ledger':ledger.to_dict('records'),'missing':missing.iloc[:,0].to_dict(),
                  'absorbed':absorbed,'absorption_ratios':dict(zip(terms,ratios)),'kept':keep,'parameters':K,
                  'all_coef':allcoef.to_dict('records'),'coef':allcoef.loc[allcoef.term.isin(['const',*keep])].to_dict('records'),
                  'warnings':model['warnings'],'covariance_min_eigenvalue_full':float(full_eigs.min()),
                  'covariance_negative_diagonal_full':int((diag<0).sum()),
                  'covariance_negative_diagonal_economic':[keep[j] for j,v in enumerate(np.diag(eco)) if v<0],
                  'covariance_min_eigenvalue_scaled_economic':float(scaled_eig.min()),
                  'covariance_economic_psd_tol1e8':bool(scaled_eig.min()>=-1e-8),
                  'independent_covariance_max_abs_error':maxerr,'cov_economic':eco.tolist(),
                  'fwl_slopes_max_abs_error':float(np.max(np.abs(beta-model['coefficients'].loc[keep,'coef'].to_numpy()))),
                  'singleton_municipalities':int(d.groupby('codigo_ibge').size().eq(1).sum()),
                  'source_fingerprint':hashlib.sha256(json.dumps(plan,sort_keys=True).encode()).hexdigest(),'status':'ok'}
                save(path.name,record);record=clean(record);pair.append(record);records.append(record)
                interaction=next((v for v in record['coef'] if ' × ' in v['term']),None)
                print(f'{rid}: N={s["N"]}, p interação={interaction["p"] if interaction else "base"}, diagonais negativas={record["covariance_negative_diagonal_full"]}',flush=True)
            except Exception as e:
                failures.append({'id':rid,'error':str(e),'traceback':traceback.format_exc()});save('falhas.json',failures);print(rid+': '+str(e),flush=True)
        if len(pair)==2:
            np.testing.assert_allclose([c['coef'] for c in pair[0]['coef']],[c['coef'] for c in pair[1]['coef']],rtol=0,atol=1e-12)
            assert pair[0]['summary']['R2']==pair[1]['summary']['R2']
    save('resultados_robustez.json',records);save('falhas.json',failures)
    for filename,digest in sources.items():assert sha256(APP/filename)==digest
    metadata={'plan':plan,'data':data,'date':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
      'python':sys.version,'python_executable':sys.executable,'numpy':np.__version__,'pandas':pd.__version__,'statsmodels':statsmodels.__version__,
      'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':'main','fits':len(records),'failures':len(failures)}
    save('metadata_robustez.json',metadata)
    assert len(records)==16 and not failures
    print('16 ajustes concluídos e covariâncias verificadas independentemente.',flush=True)
if __name__=='__main__':run()
