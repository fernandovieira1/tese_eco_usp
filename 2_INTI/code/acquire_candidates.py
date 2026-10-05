"""Discover source resources; do not silently select a final empirical definition."""
from data_paths import data_path
import json
from urllib.parse import urljoin
from acquire_h1_h2 import get
from inspect_h1_h2_sources import links
from data_common import DATA

def run():
    docs=[
      ('ibama_embargos','https://dadosabertos.ibama.gov.br/api/3/action/package_show?id=fiscalizacao-termo-de-embargo','json'),
      ('gaez_listing','https://storage.googleapis.com/gaez-v4-data?prefix=data/&delimiter=/','xml'),
      ('conab_agricolas','https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao/copy_of_agricolas','html'),
      ('era5land','https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means?tab=overview','html'),
      ('copdem','https://registry.opendata.aws/copernicus-dem/','html'),
      ('mma_cerrado','https://antigo.mma.gov.br/informma/item/7488-mma-publica-lista-de-municipios-prioritarios-do-cerrado.html','html'),
      ('mma_historico2021','https://www.gov.br/mma/pt-br/assuntos/controle-ao-desmatamento-queimadas-e-ordenamento-ambiental-territorial/controle-de-desmatamento-e-incendios-florestais/pdf/Listagemmunicpiosprioritriosparaaesdepreveno2021.pdf/@@download/file','pdf'),
      ('zarc_mt','https://www.gov.br/agricultura/pt-br/assuntos/riscos-seguro/programa-nacional-de-zoneamento-agricola-de-risco-climatico/portarias/2025-2026/mato-grosso-mt','html'),
      ('imea_metodologia','https://www.imea.com.br/imea-site/view/uploads/metodologia/custos/CustosCustoProducao2020.pdf','pdf'),
      ('inmet','https://portal.inmet.gov.br/dadoshistoricos','html'),
      ('bcb_sicor','https://www.bcb.gov.br/estabilidadefinanceira/tabelas-credito-rural-proagro','html'),
      ('mapbiomas_transitions','https://data.mapbiomas.org/api/search?q=transition&type=dataset','json'),
    ]
    for name,url,ext in docs:
        get(url,f'raw/tabular/source_documents/{name}_20260930.{ext}',name)
    p=data_path('raw/tabular/source_documents/ibama_embargos_20260930.json')
    if p.exists():
        a=json.loads(p.read_text(encoding='utf-8'))
        for r in a['result']['resources']:
            print('EMBARGO_RESOURCE',r['name'],r['url'],flush=True)
            if r['url'].endswith('/termo_embargo_csv.zip'):
                get(r['url'],'raw/tabular/ibama/termo_embargo_csv.zip','IBAMA','snapshot 2026-09-30')
    p=data_path('raw/tabular/source_documents/conab_agricolas_20260930.html')
    if p.exists(): print('CONAB_LINKS',[u for u in links(p) if any(t in u.lower() for t in ['soja','milho'])])

if __name__=='__main__': run()
