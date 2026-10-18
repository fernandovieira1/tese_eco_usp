"""Lote exploratório local. Execute com o Python .venv do repositório, a partir de pt_h1.
Primeiro grava plano imutável; depois estima via h1lab.models.fit_model. Sem FE.
"""
from pathlib import Path
import os, sys, json, hashlib, subprocess, platform, datetime, traceback
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
HERE=Path(__file__).resolve().parent
APP=HERE.parent
sys.path.insert(0,str(APP))
import numpy as np
import pandas as pd
import statsmodels
from h1lab.data import load_data, ROOT, CSV, DICIO, normalize_flag, sha256
from h1lab.models import fit_model, calendar_lag
from h1lab.ui import pretty

FILTERS={'years':[2001,2024],'biomes':['Amazônia','Cerrado','Pantanal'],'municipalities':[]}
stamp=lambda: datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).isoformat()
def dump(p,x):
    Path(p).write_text(json.dumps(x,ensure_ascii=False,indent=2,default=lambda v: v.item() if isinstance(v,np.generic) else str(v),allow_nan=False),encoding='utf-8')
def clean(x):
    if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [clean(v) for v in x]
    if isinstance(x,np.generic): x=x.item()
    if isinstance(x,float) and not np.isfinite(x): return None
    return x

# Exactly fifty hypotheses per destination, hand defined by mechanism, not a search.
# P primary price; Q alternative-use price; C GAEZ; D historical PAM; H herd;
# S initial native stock; A mapped municipal area in 2000; E/I/F IBAMA; W climate.
TEMPLATES=[
('Referência preços','P'),('Preços alternativos','Q'),('Capacidade potencial','C'),
('Capacidade histórica','D'),('Escala pecuária','H'),('Vegetação disponível','S'),
('Fiscalização espacial','E'),('Clima antecedente','W'),('Relevo','T'),('Escala territorial','A'),
('Retornos e capacidade','P C'),('Retornos e capacidade histórica','P D'),
('Usos alternativos','P Q'),('Escala pecuária e retornos','P H'),
('Vegetação e retornos','P S'),('Escala territorial e retornos','P A'),
('Retornos e fiscalização','P E'),('Retornos e clima','P W'),
('Capacidade e fiscalização','C E'),('Capacidade e escala','C S A'),
('Retornos e duas escalas','P C S A'),('Retornos, escala e clima','P C S A W'),
('Retornos, escala e relevo','P C S A T'),('Usos alternativos e escala','P Q C S A'),
('Pecuária e escala','P H C S A'),('Capacidade histórica e escala','P D S A'),
('Usos alternativos e clima','P Q C S A W'),('Clima e relevo','P C S A W T'),
('Composição territorial','P C S A B'),('Clima e pecuária','P H C S A W'),
('Fiscalização espacial e escala','P C E S A'),('Fiscalização informada e escala','P C I S A'),
('Multas observadas e escala','P C F S A'),('Fiscalização, clima e escala','P C E S A W'),
('Fiscalização e usos alternativos','P Q C E S A'),('Fiscalização e pecuária','P H C E S A'),
('Fiscalização e capacidade histórica','P D E S A'),('Multas, clima e escala','P C F S A W'),
('Fiscalização e composição territorial','P C E S A B'),('Fiscalização informada e clima','P C I S A W'),
('Preço × capacidade','P C'),('Preço × capacidade e escala','P C S A W'),
('Preço × capacidade histórica','P D S A'),('Preço × capacidade e usos alternativos','P Q C S A'),
('Preço × capacidade com fiscalização','P C E S A'),('Preço × fiscalização','P C E S A W'),
('Preço × fiscalização informada','P C I S A W'),('Preço × pecuária','P C H S A W'),
('Preço × composição territorial','P C B S A W'),('Capacidade × fiscalização','P C E S A W')]
INTERACTIONS={41:('P','C'),42:('P','C'),43:('P','D'),44:('P','C'),45:('P','C'),46:('P','E'),47:('P','I'),48:('P','H'),49:('P','B'),50:('C','E')}
REFS={
'retornos':'Angelsen (2010); Berman et al. (2023); Lubowski et al. (2008); Bragança (2018). 2_INTI/chapters/chap1/text/1_literature_review.tex, subseção Preços, capacidade produtiva e usos alternativos da terra; introdução REF7–REF8.',
'instituicoes':'Assunção et al. (2023); Harding et al. (2021); Sousa (2016); Jung et al. (2022); Probst et al. (2020). 1_literature_review.tex, subseções Instituições, implementação e respostas aos incentivos e Fiscalização e pressão econômica em Mato Grosso; introdução REF9.',
'territorio':'Chomitz e Thomas (2003); Pfaff (1999); VanWey et al. (2013); Simões et al. (2020); Seidl et al. (2001). 1_literature_review.tex, subseções Preços, capacidade produtiva e usos alternativos da terra e Heterogeneidade territorial e contribuição do artigo; introdução REF10.'}

def aliases(activity):
    crop='soja' if activity=='agricultura' else 'milho'
    suffix='soy' if crop=='soja' else 'mze'
    main='soja' if activity=='agricultura' else 'carne_bovina'
    rival='milho' if activity=='agricultura' else 'soja'
    return {
      'P':(f'ln_preco_real_usd2024_media_anual_lag1__{main}','level',0),
      'Q':(f'ln_preco_real_usd2024_media_anual_lag1__{rival}','level',0),
      'C':(f'capacidade_z__{crop}__gaez_sxHr0_{suffix}','level',0),
      'D':(f'capacidade_z__{crop}__pam_1991_2000_min7','level',0),
      'H':('efetivo_bovino_lag1','log1p',0),
      'S':('y_nativa_inicial_ha','log',0),'A':('area_referencia_ha','log',0),
      'E':('n_autos_desmatamento_lag1__ibama_espacial','log1p',0),
      'I':('n_autos_desmatamento_lag1__ibama_informada','log1p',0),
      'F':('multas_desmatamento_reais_observadas_lag1__ibama_espacial','log1p',0),
      'W':('precip_anomaly_1981_2000','level',1),
      'T':('elevation_mean_m','level',0),'B':('biome_cerrado_share_i','level',0)}

def expression(col,spec):
    s=pretty(col)
    if spec.get('lags',{}).get(col): s=f'L{spec["lags"][col]} por ano civil de ({s})'
    tr=spec.get('transforms',{}).get(col,'level')
    return f'ln({s})' if tr=='log' else f'ln(1+{s})' if tr=='log1p' else s

def plan():
    out=[]
    for y in ['conversao_ha__agricultura','conversao_ha__pastagem','taxa_conversao__agricultura','taxa_conversao__pastagem']:
        activity=y.split('__')[1]; a=aliases(activity)
        for local,(family,letters) in enumerate(TEMPLATES,1):
            keys=letters.split(); xs=[a[k][0] for k in keys]
            spec={'y':y,'xs':xs,'fe':'none','cov':'cluster_entity','require_y':True,
                  'transforms':{a[k][0]:a[k][1] for k in keys},'lags':{a[k][0]:a[k][2] for k in keys},
                  'interactions':[[a[k][0] for k in INTERACTIONS[local]]] if local in INTERACTIONS else []}
            description=' + '.join([expression(c,spec) for c in xs]+[f'({expression(l,spec)}) × ({expression(r,spec)})' for l,r in spec['interactions']])
            rationale=('Agricultura: soja como incentivo principal, milho como alternativa/complemento e GAEZ soja como aptidão.' if activity=='agricultura' else 'Pastagem: carne como incentivo principal; soja como uso alternativo; GAEZ milho indica oportunidade agrícola/alimentação, não aptidão de pasto. Rebanho antecedente mede escala pecuária.')
            rationale+=' '+family+'. '
            if 'S' in keys: rationale+='Vegetação no início do intervalo controla a exposição à abertura. '
            if 'A' in keys: rationale+='Área mapeada em 2000 controla escala fixa sem usar identificadores. '
            if any(k in keys for k in ['E','I','F']): rationale+='Registros em t−1 aproximam atuação administrativa, com seleção por pressão e cobertura parcial. '
            if local in INTERACTIONS: rationale+='Produto após transformações, com ambos os componentes; permite inclinação heterogênea prevista em H1. '
            if local<=10: rationale+='Referência univariada; não controla confundimento. '
            signs='Preço próprio: positivo condicional; alternativa agrícola: ambíguo por substituição/complementaridade; capacidade agrícola: positivo na agricultura, ambíguo na pastagem; fiscalização e sua interação com preço: potencial contenção, mas sinal observado indeterminado por seleção; estoque e escala: geralmente positivos em ha, ambíguos em taxas; clima/relevo: sem sinal imposto.'
            refs=REFS['retornos']+' '+REFS['territorio']+(' '+REFS['instituicoes'] if any(k in keys for k in ['E','I','F']) else '')
            out.append({'id':f'M{len(out)+1:03}','local':local,'family':family,'keys':keys,'spec':spec,'description':description,'rationale':rationale,'signs':signs,'refs':refs})
    signatures=[json.dumps([p['spec']['y'],sorted(p['spec']['xs']),p['spec']['transforms'],p['spec']['lags'],p['spec']['interactions']],sort_keys=True) for p in out]
    assert len(out)==200 and len(set(signatures))==200
    return out

def sample_id(sample):
    return hashlib.sha256(sample[['codigo_ibge','ano']].sort_values(['codigo_ibge','ano']).to_csv(index=False).encode()).hexdigest()

def run():
    full,cat,meta=load_data()
    planned=plan()
    planned_path=HERE/'plano_pre_estimacao.json'
    initial={'created':stamp(),'filters':FILTERS,'source':meta,'models':planned}
    if planned_path.exists():
        old=json.loads(planned_path.read_text(encoding='utf-8'))
        assert old['models']==planned and old['source']['csv_sha256']==meta['csv_sha256'], 'Plano/fonte mudou; use diretório de execução novo.'
        initial=old
    else: dump(planned_path,initial)
    # No regressions have been examined before this persisted plan.
    results=[]; failures=[]
    for i,p in enumerate(planned,1):
        path=HERE/(p['id']+'.json')
        if path.exists():
            record=json.loads(path.read_text(encoding='utf-8'))
            assert record['plan']==p
        else:
            try:
                r=fit_model(full,FILTERS,p['spec']); s=r['summary']; sample=r['sample']
                assert r['design'].shape[1]==len(r['terms'])+1
                assert s['Graus de liberdade residuais']>1
                coef=r['coefficients'].reset_index().to_dict('records')
                diag=r['diagnostics']
                ibama={}
                for col in p['spec']['xs']:
                    if 'ibama' in col:
                        flag=col.replace('n_autos_desmatamento','flag_contagem_desmatamento_parcial').replace('multas_desmatamento_reais_observadas','flag_soma_desmatamento_parcial')
                        if flag in sample: ibama[flag]=int(normalize_flag(sample[flag]).fillna(False).sum())
                sample[['codigo_ibge','ano']].to_csv(HERE/(p['id']+'_amostra.csv'),index=False)
                record={'plan':p,'status':'ok','estimated':stamp(),'summary':s,'coef':coef,
                        'sample_id':sample_id(sample),'sample_min':int(sample.ano.min()),'sample_max':int(sample.ano.max()),
                        'municipalities':sorted(sample.codigo_ibge.unique().tolist()),
                        'years':sample.groupby('ano').size().to_dict(),'biomes':sample.groupby('bioma_dominante').size().to_dict(),
                        'ledger':r['ledger'].to_dict('records'),'missing':r['missing'].iloc[:,0].to_dict(),
                        'warnings':r['warnings'],'partial_ibama':ibama,
                        'max_cook':float(diag.Cook.max()),'cooks_gt_4n':int(diag.Cook.gt(4/len(sample)).sum()),
                        'pred_negative':int(diag.ajustado.lt(0).sum()),'pred_gt1':int(diag.ajustado.gt(1).sum()) if p['spec']['y'].startswith('taxa') else None,
                        'vif':r['vif'].reset_index().to_dict('records')}
            except Exception as e:
                record={'plan':p,'status':'failed','error':str(e),'traceback':traceback.format_exc()}
            dump(path,clean(record))
        (results if record['status']=='ok' else failures).append(record)
        if i%25==0: print(f'{i}/200 | válidas={len(results)} | falhas={len(failures)}',flush=True)
    dump(HERE/'falhas.json',failures)
    # Candidatas por conteúdo: baseline controlada, interação de capacidade e institucional.
    # No optimization by R2 or p. Common-sample re-estimates are separate and not counted.
    comparisons=[]
    for y in sorted({r['plan']['spec']['y'] for r in results}):
        candidates=[r for r in results if r['plan']['spec']['y']==y and r['plan']['local'] in [22,42,46]]
        keysets=[set(map(tuple,pd.read_csv(HERE/(r['plan']['id']+'_amostra.csv'),dtype={'codigo_ibge':str}).values.tolist())) for r in candidates]
        common=set.intersection(*keysets)
        reduced=full.copy()
        # Preserve prior calendar years for X lags; mask only Y outside intersection.
        reduced.loc[[tuple(x) not in common for x in full[['codigo_ibge','ano']].values.tolist()],y]=np.nan
        for c in candidates:
            r=fit_model(reduced,FILTERS,c['plan']['spec'])
            assert len(r['sample'])==len(common)
            comparisons.append({'id':'CC_'+c['plan']['id'],'original':c['plan']['id'],'summary':r['summary'],
                 'sample_id':sample_id(r['sample']),'coef':r['coefficients'].reset_index().to_dict('records'),
                 'min':int(r['sample'].ano.min()),'max':int(r['sample'].ano.max()),
                 'municipalities':sorted(r['sample'].codigo_ibge.unique().tolist())})
    dump(HERE/'amostra_comum.json',clean(comparisons))
    # Verify original rates numerically and report actual availability.
    ratio_checks={}
    for a in ['agricultura','pastagem']:
        rate=full[f'taxa_conversao__{a}']; calc=full[f'conversao_ha__{a}']/full.y_nativa_inicial_ha.where(full.y_nativa_inicial_ha.gt(0))
        ratio_checks[a]={'max_abs_difference':float((rate-calc).abs().max()),'nonpositive_denominator':int(full.y_nativa_inicial_ha.le(0).sum())}
    version=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    metadata={'started':initial['created'],'finished':stamp(),'meta':meta,'git_head':version,
      'git_branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),
      'python':sys.version,'python_executable':sys.executable,'numpy':np.__version__,'pandas':pd.__version__,'statsmodels':statsmodels.__version__,
      'code_hashes':{str(p.relative_to(ROOT)):sha256(p) for p in [APP/'app.py',APP/'h1lab/data.py',APP/'h1lab/models.py',APP/'h1lab/model_view.py']},
      'ratio_checks':ratio_checks,'valid':len(results),'failed':len(failures)}
    assert metadata['git_branch']=='main'
    dump(HERE/'metadata.json',metadata)
    dump(HERE/'resultados_completos.json',clean(results))
    print('Lote concluído. Conferir dashboard e montar Excel.',flush=True)

if __name__=='__main__': run()
