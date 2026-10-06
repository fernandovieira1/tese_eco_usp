"""Copernicus GLO-90 original COG tiles intersecting the existing MT geometry.

The source is a surface model (DSM); do not interpret it as bare-earth terrain.
"""
import math,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import geopandas as gpd
from shapely.geometry import box
from data_common import DATA,fetch

def tile(pair):
    lat,lon=pair;stem=f'Copernicus_DSM_COG_30_S{abs(lat):02d}_00_W{abs(lon):03d}_00_DEM'
    manifest=f'acquisition_dem_{abs(lat)}_{abs(lon)}.jsonl'
    try:
        listing=fetch('https://copernicus-dem-90m.s3.amazonaws.com/?list-type=2&prefix='+stem,'raw/raster/copdem90/metadata/'+stem+'.xml','Copernicus','GLO-90',manifest=manifest)
        root=ET.parse(listing);ns={'s':'http://s3.amazonaws.com/doc/2006-03-01/'}
        keys=[x.text for x in root.findall('.//s:Key',ns)]
        for key in keys:
            if key.endswith('/'+stem+'.tif'):
                fetch('https://copernicus-dem-90m.s3.amazonaws.com/'+key,'raw/raster/copdem90/'+stem+'.tif','Copernicus','GLO-90 original COG',manifest=manifest)
                return True
        return False
    except Exception as e:print('DEM FALHA',stem,str(e)[:140],flush=True);return False

if __name__=='__main__':
    m=gpd.read_file('zip://'+str(DATA/'raw/vector/ibge/MT_Municipios_2024.zip')).to_crs(4326).geometry.union_all()
    x0,y0,x1,y1=m.bounds
    tiles=[(lat,lon) for lat in range(math.floor(y0),math.ceil(y1)) for lon in range(math.floor(x0),math.ceil(x1)) if box(lon,lat,lon+1,lat+1).intersects(m)]
    with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(tile,tiles))
    print('DEM',sum(results),'/',len(tiles),flush=True)
