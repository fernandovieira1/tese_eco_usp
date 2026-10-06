"""Explicit GAEZ v4 alternatives: 1961-1990, rainfed, no CO2, high/low inputs.

sx is a continuous suitability index (0-10000), not categorical si.
yx is attainable yield of the best suitability class, not realized PAM yield.
"""
import xml.etree.ElementTree as ET
from acquire_h1_h2 import get
from acquire_raster_candidates import listing
ns={'s':'http://doc.s3.amazonaws.com/2006-03-01'}
if __name__=='__main__':
    for management in ['H','L']:
        for variable in ['sx','yx']:
            prefix=f'data/res05/CRUTS32/Hist/6190{management}/{variable}{management}r0_'
            p=listing(prefix,f'gaez_{variable}{management}r0_listing')
            if not p:continue
            for node in ET.parse(p).findall('.//s:Key',ns):
                key=node.text
                if any(key.endswith(f'_{crop}.tif') for crop in ['soy','mze']):
                    get('https://storage.googleapis.com/gaez-v4-data/'+key,'raw/raster/gaez_v4_6190/'+key.split('/')[-1],'FAO/IIASA',f'v4; CRUTS32 1961-1990; inputs={management}; rainfed; sem fertilizacao CO2')
