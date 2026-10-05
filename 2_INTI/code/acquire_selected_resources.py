from data_paths import data_path
import json
from acquire_h1_h2 import get
from data_common import DATA
from inspect_h1_h2_sources import links

def main():
    for u in links(data_path('raw/tabular/source_documents/conab_milho_20260930.html')):
        if '.xls' in u and 'milho' in u:
            u=u.removesuffix('/view');get(u,'raw/tabular/conab/'+u.split('/')[-1],'CONAB','series historicas separadas por safra')
    get('https://storage.googleapis.com/gaez-v4-data?prefix=data/res05/CRUTS32/&delimiter=/','raw/tabular/source_documents/gaez_historical_listing.xml','FAO/IIASA','GAEZ v4')
    get('https://copernicus-dem-90m-stac.s3.amazonaws.com/catalog.json','raw/tabular/source_documents/copdem90_catalog.json','Copernicus','GLO-90 candidato para controle')
    get('https://data.mapbiomas.org/api/datasets/:persistentId/?persistentId=doi:10.58053/MapBiomas/2W2Z5M','raw/tabular/source_documents/mapbiomas_col9_transitions_metadata.json','MapBiomas Brasil','9; alternativa separada')
    get('https://dadosabertos.ibama.gov.br/api/3/action/package_show?id=termos-de-embargo','raw/tabular/source_documents/ibama_termos_alternativo.json','IBAMA')
    for n in ['mapbiomas_col9_transitions_metadata','ibama_termos_alternativo','copdem90_catalog']:
        p=data_path(f'raw/tabular/source_documents/{n}.json')
        if p.exists():
            a=json.loads(p.read_text(encoding='utf-8'))
            if n.startswith('mapbiomas'):
                print('MB_FILES',[(r['dataFile']['id'],r['label'],r['dataFile']['filesize']) for r in a['data']['latestVersion']['files']],flush=True)
            elif n.startswith('ibama'):print('IBAMA_ALT',[(r['name'],r['url']) for r in a['result']['resources']],flush=True)
            else:print('DEM_LINKS',a.get('links',[])[:5],flush=True)

if __name__=='__main__':main()
