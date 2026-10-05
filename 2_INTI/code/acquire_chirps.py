"""CHIRPS v2 candidate vintage; downloads complete years, original compressed rasters.

Storage window 1981-2025 provides climatology inputs; does not set empirical sample.
Sequential acquisition keeps the existing manifest writer race-free.
"""
from data_paths import data_path
import re,json
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from acquire_h1_h2 import get
from inspect_h1_h2_sources import links
from data_common import DATA,fetch,sha256
from data_paths import legacy_repository_path

def year_download(year):
    for name in urls:
        m=re.fullmatch(r'chirps-v2.0.(\d{4}).(\d{2}).tif.gz',name)
        if not m or int(m[1])!=year:continue
        relative='raw/raster/chirps_v2/'+name
        p=data_path(relative)
        if p.exists():
            records=[]
            for manifest in (DATA/'catalog').glob('acquisition*.jsonl'):
                records.extend(json.loads(l) for l in manifest.read_text(encoding='utf-8').splitlines())
            assert any(r.get('sha256')==sha256(p) and legacy_repository_path(r.get('arquivo_local',''))=='2_INTI/data/'+relative for r in records)
            continue
        try:
            fetch(urljoin('https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_monthly/tifs/',name),relative,'UCSB Climate Hazards Center','CHIRPS v2.0; monthly; candidate vintage',manifest=f'acquisition_chirps_{year}.jsonl',timeout=90)
        except Exception as e:print('FALHA',name,str(e)[:160],flush=True)
    print('CHIRPS',year,'finished',flush=True)

if __name__=='__main__':
    urls=links(data_path('raw/tabular/source_documents/chirps_v2_20260930.html'))
    with ThreadPoolExecutor(max_workers=6) as pool:list(pool.map(year_download,range(1981,2026)))
