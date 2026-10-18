"""TWFE das 12 candidatas, pooled original e pooled reduzido, mesma amostra por trio.
Sem modificar h1lab. As transformações são aplicadas uma vez antes da absorção.
"""
from pathlib import Path
import os,sys,json,hashlib,datetime,subprocess,traceback
os.environ['OPENBLAS_NUM_THREADS']='1';os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent; APP=HERE.parent
sys.path.insert(0,str(APP))
import numpy as np
import pandas as pd
import statsmodels
from h1lab.data import load_data,ROOT,CSV,DICIO,sha256,KEYS
from h1lab.models import fit_model,prepare_sample
from h1lab.ui import pretty
FILTERS={'years':[2001,2024],'biomes':['Amazônia','Cerrado','Pantanal'],'municipalities':[]}
def clean(v):
    if isinstance(v,dict): return {str(k):clean(x) for k,x in v.items()}
    if isinstance(v,(list,tuple)): return [clean(x) for x in v]
    if isinstance(v,np.generic): v=v.item()
    if isinstance(v,float) and not np.isfinite(v):return None
    return v
def save(name,v): (HERE/name).write_text(json.dumps(clean(v),ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def sid(sample):return hashlib.sha256(sample[KEYS].sort_values(KEYS).to_csv(index=False).encode()).hexdigest()
def effects_design(sample):
    return pd.concat([pd.DataFrame({'const':np.ones(len(sample))}),
       *[pd.get_dummies(sample[k].astype('string'),prefix='FE_'+k,drop_first=True,dtype=float) for k in KEYS]],axis=1)
def absorbed_by(sample,term,key):
    x=sample[term].to_numpy(float)
    residual=x-sample.groupby(key)[term].transform('mean').to_numpy(float)
    return np.linalg.norm(residual)<=1e-10*max(np.linalg.norm(x),np.finfo(float).tiny)
def run():
    source=json.loads((HERE/'candidatas_origem.json').read_text(encoding='utf-8'))
    assert sha256(APP/'RESULTADOS_DASH_H1.xlsx')==source['sha256']
    assert subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip()=='main'
    full,catalog,meta=load_data()
    old=json.loads((APP/'execucao_ols_200/resultados_completos.json').read_text(encoding='utf-8'))
    originals={r['plan']['id']:r for r in old}
    candidates=source['candidates']
    planned=[]
    for row in candidates:
        mid=row['ID do modelo']; old=originals[mid]; spec=old['plan']['spec']
        assert row['Variável dependente']==pretty(spec['y'])
        assert row['Variáveis Independentes']==old['plan']['description']
        assert np.isclose(row['R2'],old['summary']['R2'],rtol=1e-12)
        planned.append({'id':mid,'original_spec':spec,'original_sample':row['ID amostra SHA256'],
             'models':['Pooled original','Pooled termos identificáveis','TWFE município + ano'],
             'rule':'Construir amostra da especificação original; projetar cada X e interação contra intercepto/dummies municipais/anuais. Retirar apenas termos individualmente absorvidos a tolerância relativa 1e-10. Nenhuma seleção por valor-p. Interações construídas antes da retirada dos componentes absorvidos.'})
    if not (HERE/'plano_fe.json').exists():save('plano_fe.json',{'created':source['created'],'source_sha256':source['sha256'],'models':planned})
    else:assert json.loads((HERE/'plano_fe.json').read_text(encoding='utf-8'))['models']==planned
    results=[];failures=[]
    for p in planned:
        mid=p['id']; target=HERE/(mid+'_fe.json')
        if target.exists():
            record=json.loads(target.read_text(encoding='utf-8'))
            assert record['plan']==p and record['data_sha256']==meta['csv_sha256']
            results.append(record);continue
        try:
            spec=p['original_spec'];pooled=fit_model(full,FILTERS,spec)
            sample=pooled['sample'];terms=pooled['terms'];F=effects_design(sample);f=F.to_numpy(float)
            assert sid(sample)==p['original_sample']
            assert np.isclose(pooled['summary']['R2'],originals[mid]['summary']['R2'],rtol=1e-12)
            x=sample[terms].to_numpy(float); residual=x-f@np.linalg.lstsq(f,x,rcond=None)[0]
            statuses=[];keep=[];drop=[]
            for j,term in enumerate(terms):
                ratio=float(np.linalg.norm(residual[:,j])/max(np.linalg.norm(x[:,j]),np.finfo(float).tiny))
                absorbed=ratio<=1e-10
                (drop if absorbed else keep).append(term)
                byentity=absorbed_by(sample,term,'codigo_ibge');byyear=absorbed_by(sample,term,'ano')
                why='Município: atributo fixo no tempo' if absorbed and byentity else 'Ano: série comum aos municípios' if absorbed and byyear else 'Combinação aditiva município + ano' if absorbed else 'Mantido: variação residual após FE de município e ano'
                statuses.append({'term':term,'absorbed':absorbed,'reason':why,'entity_absorbed':byentity,'year_absorbed':byyear,'relative_residual_norm':ratio,'within_sd':float(np.std(residual[:,j],ddof=1))})
            assert keep
            # sample already carries original transformations, calendar lags and products.
            # Level/lag0 avoids transforming/lagging twice or recalculating products.
            reduced_spec={'y':spec['y'],'xs':keep,'fe':'none','cov':'cluster_entity','require_y':True,
                        'transforms':{},'lags':{},'interactions':[]}
            reduced=fit_model(sample,FILTERS,reduced_spec)
            twfe_spec={**reduced_spec,'fe':'twoway'}
            twfe=fit_model(sample,FILTERS,twfe_spec)
            assert sid(twfe['sample'])==sid(reduced['sample'])==sid(sample)
            assert twfe['design'].shape[1]==np.linalg.matrix_rank(twfe['design'].to_numpy(float))
            # Independent FWL verification of slopes and residuals, no residual-regression SEs.
            yy=sample[spec['y']].to_numpy(float);xx=sample[keep].to_numpy(float)
            ry=yy-f@np.linalg.lstsq(f,yy,rcond=None)[0]
            rx=xx-f@np.linalg.lstsq(f,xx,rcond=None)[0]
            beta=np.linalg.lstsq(rx,ry,rcond=None)[0]
            full_beta=twfe['coefficients'].loc[keep,'coef'].to_numpy(float)
            np.testing.assert_allclose(beta,full_beta,rtol=1e-7,atol=1e-8)
            residual_fwl=ry-rx@beta
            np.testing.assert_allclose(residual_fwl,twfe['diagnostics'].residuo,rtol=1e-7,atol=1e-7)
            sse=float(np.square(twfe['diagnostics'].residuo).sum())
            sse_fe=float(ry@ry)
            assert np.isclose(1-sse/sse_fe,twfe['summary']['R2 parcial aos efeitos fixos'],rtol=1e-9)
            assert sse<=float(np.square(pooled['diagnostics'].residuo).sum())+1e-6
            fits={}
            for name,model in [('Pooled original',pooled),('Pooled termos identificáveis',reduced),('TWFE município + ano',twfe)]:
                fits[name]={'summary':model['summary'],'coef':model['coefficients'].reset_index().to_dict('records'),
                  'all_coef':model['all_coefficients'].reset_index().to_dict('records'),'terms':model['terms'],
                  'parameters':model['design'].shape[1],'sample_id':sid(model['sample']),
                  'warnings':model['warnings'],'spec':model['spec'],
                  'sse':float(np.square(model['diagnostics'].residuo).sum()),
                  'negative_predictions':int(model['diagnostics'].ajustado.lt(0).sum()),
                  'above1_predictions':int(model['diagnostics'].ajustado.gt(1).sum()) if spec['y'].startswith('taxa') else None}
            sample[KEYS+['municipio','bioma_dominante',spec['y'],*terms]].to_csv(HERE/(mid+'_amostra_transformada.csv'),index=False)
            record={'plan':p,'data_sha256':meta['csv_sha256'],'fits':fits,'absorption':statuses,
              'absorbed':drop,'kept':keep,'sample_id':sid(sample),'sample_min':int(sample.ano.min()),'sample_max':int(sample.ano.max()),
              'per_year':sample.groupby('ano').size().to_dict(),'per_biome':sample.groupby('bioma_dominante').size().to_dict(),
              'municipalities':sorted(sample.codigo_ibge.unique().tolist()),'ledger':pooled['ledger'].to_dict('records'),
              'missing':pooled['missing'].iloc[:,0].to_dict(),'refs':originals[mid]['plan']['refs'],
              'description':originals[mid]['plan']['description'],'rationale':originals[mid]['plan']['rationale'],
              'partial_ibama':originals[mid]['partial_ibama'],'fwl_beta_max_error':float(np.max(np.abs(beta-full_beta))),
              'fwl_residual_max_error':float(np.max(np.abs(residual_fwl-twfe['diagnostics'].residuo.to_numpy()))),
              'fe_only_r2':float(1-sse_fe/np.square(yy-yy.mean()).sum()),'sse_fe_only':sse_fe,
              'baseline_entity':str(sample.codigo_ibge.astype('string').sort_values().iloc[0]),
              'baseline_year':str(sample.ano.astype('string').sort_values().iloc[0]),'status':'ok'}
            save(target.name,record);results.append(clean(record))
            print(f'{mid}: N={len(sample)}, absorvidos={len(drop)}, mantidos={len(keep)}, R2parcial={twfe["summary"]["R2 parcial aos efeitos fixos"]:.6f}',flush=True)
        except Exception as e:
            failures.append({'id':mid,'error':str(e),'traceback':traceback.format_exc()})
            save('falhas.json',failures); print(f'{mid}: falha {e}',flush=True)
    save('resultados_fe.json',results);save('falhas.json',failures)
    assert sha256(APP/'RESULTADOS_DASH_H1.xlsx')==source['sha256']
    metadata={'source':source,'data':meta,'filters':FILTERS,'date':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat(),
       'python':sys.version,'python_executable':sys.executable,'numpy':np.__version__,'pandas':pd.__version__,'statsmodels':statsmodels.__version__,
       'git_head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'branch':'main','valid_candidates':len(results),'fits':len(results)*3,'failures':len(failures),
       'code_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [APP/'h1lab/models.py',APP/'h1lab/data.py',APP/'app.py']}}
    save('metadata_fe.json',metadata)
    assert len(results)==12 and not failures
    print('12 candidatas TWFE + 24 pooled de comparação; sem falhas.',flush=True)

if __name__=='__main__':run()
