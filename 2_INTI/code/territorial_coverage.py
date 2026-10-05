"""Describe territorial support; do not invent a historical crosswalk."""
from data_paths import data_path
import json,pandas as pd
from data_common import DATA
from prepare_h1_h2 import save

if __name__=='__main__':
    lookup=json.loads((data_path('raw/tabular/ibge/municipios_mt_consulta20260928.json')).read_text(encoding='utf-8'))
    d=pd.DataFrame([{'codigo_ibge':str(r['id']),'municipio':r['nome'],'uf':'MT'} for r in lookup])
    for source,file in [('pam','h1_h2__pam_soja_milho__ibge__municipio_anual.csv'),('ppm','h1_h2__ppm_bovinos__ibge__municipio_anual.csv'),('mapbiomas10_1','h2__native_veg__mapbiomas_col10_1__candidato.csv')]:
        p=pd.read_csv(data_path('processed/tabular/'+file),dtype={'codigo_ibge':str},low_memory=False)
        d[f'presente_{source}']=d.codigo_ibge.isin(p.codigo_ibge.unique())
    d['harmonizacao_historica_validada']=False
    d['observacao']='Cadastro corrente; presenca nao implica comparabilidade historica'
    d.loc[d.municipio.isin(['Boa Esperança do Norte','Sorriso','Nova Ubiratã']),'observacao']='Verificar desmembramento Boa Esperanca do Norte; unidade composta e alternativa ainda nao adotada'
    save(d,'territorio__cobertura_fontes__sem_harmonizacao.csv')
