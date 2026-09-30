"""Source-discovered GAEZ candidates and official DEM distribution metadata."""
import json,xml.etree.ElementTree as ET
from urllib.parse import quote
from acquire_h1_h2 import get
from data_common import DATA

def listing(prefix,name):
    return get('https://storage.googleapis.com/gaez-v4-data?prefix='+quote(prefix,safe='/')+'&delimiter=/',f'raw/tabular/source_documents/{name}.xml','FAO/IIASA','GAEZ v4')

if __name__=='__main__':
    listing('data/res05/CRUTS32/Hist/','gaez_hist_periods')
    listing('data/LR/ter/','gaez_terrain')
    get('https://copernicus-dem-30m.s3.amazonaws.com/readme.html','raw/tabular/source_documents/copdem_readme.html','Copernicus')
    get('https://copernicus-dem-90m.s3.amazonaws.com/?list-type=2&prefix=Copernicus_DSM_COG_30_S14_00_W056_00','raw/tabular/source_documents/copdem90_listing.xml','Copernicus','GLO-90')
    get('https://data.mapbiomas.org/api/access/datafile/232','raw/tabular/mapbiomas/collection9_coverage_transitions.xlsx','MapBiomas Brasil','9; DOI 2W2Z5M; alternativa nao combinada a 10.1')
    get('https://pamgia.ibama.gov.br/geoservicos/arquivos/adm_embargo_ibama_a.shp.zip','raw/vector/ibama/adm_embargo_ibama_a.shp.zip','IBAMA','snapshot; nao retroceder estoque')
