"""Additive acquisition. Reuses data_common.fetch; run with --stage core/pages.

Raw data and HTTP failure evidence remain under 2_INTI/data. No sample is selected.
"""
import argparse
from data_common import fetch

PAGES = {
 'worldbank': 'https://www.worldbank.org/en/research/commodity-markets',
 'ibama_autos': 'https://dadosabertos.ibama.gov.br/api/3/action/package_show?id=fiscalizacao-auto-de-infracao',
 'ibama_embargos': 'https://dadosabertos.ibama.gov.br/api/3/action/package_show?id=fiscalizacao-area-embargada',
 'gaez_v4': 'https://www.fao.org/gaez/gaezv4/en',
 'chirps_v2': 'https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/',
 'mma_amazonia': 'https://www.gov.br/mma/pt-br/assuntos/controle-ao-desmatamento-queimadas-e-ordenamento-ambiental-territorial/controle-do-desmatamento-1/municipios-prioritarios-da-amazonia',
 'conab_precos': 'https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/precos-agropecuarios',
 'cepea': 'https://cepea.org.br/indicador/',
 'gaez_files': 'https://gaez-v4-data.fao.org/data/',
 'ibama_packages': 'https://dadosabertos.ibama.gov.br/api/3/action/package_list',
 'conab_custos': 'https://www.gov.br/conab/pt-br/atuacao/informacoes-agropecuarias/custos-de-producao/planilhas-de-custos-de-producao',
 'car': 'https://www.gov.br/car/pt-br/central-de-conteudo/boletins-informativos-do-car',
 'imea': 'https://wap.imea.com.br/imea-site/relatorios-mercado',
}

def get(url, path, source, version='consulta 2026-09-30'):
    try:
        p = fetch(url, path, source, version, manifest='acquisition_h1_h2.jsonl', timeout=90)
        print('OK', p.name, p.stat().st_size, flush=True)
        return p
    except Exception as exc:
        print('FALHA', path, str(exc)[:220], flush=True)

def core():
    for table, variables, classification in [('1612','109|216|214|112','81[2711,2713]'), ('3939','105','79[2670]')]:
        # All periods advertised by the source; this is storage coverage, not an empirical sample.
        for start in range(1974,2026,10):
            end=min(start+9,2025)
            url=f'https://servicodados.ibge.gov.br/api/v3/agregados/{table}/periodos/{start}-{end}/variaveis/{variables}?localidades=N6[N3[51]]&classificacao={classification}'
            get(url,f'raw/tabular/ibge/t{table}_{start}_{end}.json','IBGE/PAM' if table=='1612' else 'IBGE/PPM','API v3; valores originais')
    get('https://data.mapbiomas.org/api/access/datafile/535','raw/tabular/mapbiomas/collection10_1_coverage.xlsx','MapBiomas Brasil','10.1; datafile 535; DOI SJZOLT')
    get('https://geoftp.ibge.gov.br/informacoes_ambientais/estudos_ambientais/biomas/vetores/Biomas_250mil.zip','raw/vector/ibge/Biomas_250mil_2019.zip','IBGE','2019; alternativa explicita, nao substitui vintage')

def extra():
    import json
    from data_common import DATA
    from inspect_h1_h2_sources import links
    d=DATA/'raw/tabular/source_documents'
    for url in links(d/'worldbank_20260930.html'):
        if 'Monthly.xlsx' in url:
            get(url,'raw/tabular/worldbank/pink_sheet_monthly_20260930.xlsx','Banco Mundial','snapshot 2026-09-30; nominal USD')
    a=json.loads((d/'ibama_autos_20260930.json').read_text(encoding='utf-8'))
    for r in a['result']['resources']:
        if r['url'].endswith('/auto_infracao_csv.zip'):
            get(r['url'],'raw/tabular/ibama/auto_infracao_csv.zip','IBAMA','snapshot 2026-09-30')
    for name in ['gaez_files','ibama_packages','conab_custos','car','imea']:
        get(PAGES[name],f'raw/tabular/source_documents/{name}_20260930.'+('json' if name.startswith('ibama') else 'html'),name)

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--stage',choices=['core','pages','extra'],required=True)
    args=parser.parse_args()
    if args.stage=='core': core()
    elif args.stage=='extra': extra()
    else:
        for name,url in PAGES.items():
            get(url,f'raw/tabular/source_documents/{name}_20260930.'+('json' if name.startswith('ibama') else 'html'),name)
