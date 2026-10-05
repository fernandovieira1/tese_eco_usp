from data_paths import data_path
import json
from acquire_h1_h2 import get
from inspect_h1_h2_sources import links
from data_common import DATA

def main():
    p=data_path('raw/tabular/source_documents/ibama_embargos_20260930.json')
    for r in json.loads(p.read_text(encoding='utf-8'))['result']['resources']:
        if r['url'].endswith(('/termo_de_embargo.csv','/termo_de_embargo_coordenadas.csv','/termo_embargo_historico.csv')):
            get(r['url'],'raw/tabular/ibama/'+r['url'].split('/')[-1],'IBAMA','snapshot 2026-09-30')
    for u in links(data_path('raw/tabular/source_documents/conab_agricolas_20260930.html')):
        if u.endswith('.xls') and 'soja' in u:
            get(u,'raw/tabular/conab/'+u.split('/')[-1],'CONAB','1997-2026; custos heterogeneos por local e tecnologia')
        if u.endswith('/milho'):
            p=get(u,'raw/tabular/source_documents/conab_milho_20260930.html','CONAB')
            if p:
                for x in links(p):
                    if x.endswith(('.xls','.xlsx')):get(x,'raw/tabular/conab/'+x.split('/')[-1],'CONAB')
    for u in links(data_path('raw/tabular/source_documents/zarc_mt_20260930.html')):
        if 'SOJA' in u.upper():get(u.removesuffix('/view'),'raw/tabular/source_documents/zarc_soja_mt_2025_2026.pdf','MAPA','Portaria 372; 2025/2026')
    for prefix in ['res05','LR','documentation']:
        get(f'https://storage.googleapis.com/gaez-v4-data?prefix=data/{prefix}/&delimiter=/',f'raw/tabular/source_documents/gaez_{prefix}_listing.xml','FAO/IIASA','GAEZ v4')
    get('https://data.mapbiomas.org/api/search?q=municipalities&type=dataset&per_page=100','raw/tabular/source_documents/mapbiomas_municipalities.json','MapBiomas Brasil')

if __name__=='__main__':main()
