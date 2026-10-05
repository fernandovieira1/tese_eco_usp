"""Candidate monthly zonal CHIRPS means on 2024 municipal boundaries.

Pixel-centre assignment, cosine latitude weights; retain cropped GeoTIFFs.
Calendar-year anomalies are candidates, not an adopted soybean growing season.
"""
import gzip,re,math
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.io import MemoryFile
from rasterio.windows import from_bounds,transform as win_transform,Window
from rasterio.features import rasterize
from data_common import DATA,write_json
from prepare_h1_h2 import save

def main():
    m=gpd.read_file('zip://'+str(DATA/'raw/vector/ibge/MT_Municipios_2024.zip')).to_crs(4326).sort_values('CD_MUN').reset_index(drop=True)
    rows=[];info=[];labels=None
    out=DATA/'interim/raster/chirps_v2_mt_fullbounds';out.mkdir(parents=True,exist_ok=True)
    for p in sorted((DATA/'raw/raster/chirps_v2').glob('*.tif.gz')):
        year,month=map(int,re.search(r'(\d{4}).(\d{2}).tif',p.name).groups())
        target=out/p.name.removesuffix('.gz')
        with rasterio.open('/vsigzip/'+p.resolve().as_posix()) as original:
            original_info={'crs':str(original.crs),'bbox':list(original.bounds),'resolucao':list(original.res),'nodata':original.nodata,'bandas':original.count,'width':original.width,'height':original.height}
        if not target.exists():
            with gzip.open(p,'rb') as f,MemoryFile(f.read()) as mem,mem.open() as src:
                w=from_bounds(*m.total_bounds,transform=src.transform)
                window=Window(math.floor(w.col_off),math.floor(w.row_off),math.ceil(w.col_off+w.width)-math.floor(w.col_off),math.ceil(w.row_off+w.height)-math.floor(w.row_off))
                arr=src.read(1,window=window);tr=win_transform(window,src.transform)
                profile=src.profile.copy();profile.update(height=arr.shape[0],width=arr.shape[1],transform=tr,compress='deflate')
                with rasterio.open(target,'w',**profile) as dst:dst.write(arr,1)
        with rasterio.open(target) as src:
            a=src.read(1); tr=src.transform
            if labels is None:
                labels=rasterize([(g,i+1) for i,g in enumerate(m.geometry)],out_shape=a.shape,transform=tr,fill=0,dtype='int16')
                lat=tr.f+(np.arange(a.shape[0])+.5)*tr.e
                weights=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],a.shape)
            valid=(a!=src.nodata)&np.isfinite(a)&(a>=0)&(labels>0)
            num=np.bincount(labels[valid],weights=(a*weights)[valid],minlength=len(m)+1)
            den=np.bincount(labels[valid],weights=weights[valid],minlength=len(m)+1)
            total=np.bincount(labels.ravel(),weights=weights.ravel(),minlength=len(m)+1)
            values=np.divide(num,den,out=np.full(num.shape,np.nan),where=den>0)
            for i,r in m.iterrows():rows.append({'codigo_ibge':r.CD_MUN,'municipio':r.NM_MUN,'ano':year,'mes':month,'precip_mm':values[i+1],'fracao_pixels_validos':den[i+1]/total[i+1] if total[i+1]>0 else None})
            info.append({'arquivo':str(p.relative_to(DATA)),'original':original_info,'recorte':str(target.relative_to(DATA)),'crs':str(src.crs),'resolucao':list(src.res),'nodata':src.nodata,'bbox':list(src.bounds),'bandas':src.count,'min':float(a[valid].min()),'max':float(a[valid].max()),'tratamento_nodata':'exclui negativos, inclusive -9999 oficial, quando tag NoData ausente'})
    d=pd.DataFrame(rows);save(d,'h2__precip_mm__chirps_v2__mensal_candidato.csv')
    a=d.groupby(['codigo_ibge','ano']).precip_mm.agg(['sum','count']).reset_index()
    a['precip_mm_anual']=a['sum'].where(a['count']==12)
    for start,end in [(1981,2010),(1991,2020)]:
        base=a[a.ano.between(start,end)].groupby('codigo_ibge').precip_mm_anual.agg(['mean','std','count'])
        a=a.join(base.add_suffix(f'_{start}_{end}'),on='codigo_ibge')
        a[f'precip_anomaly_{start}_{end}']=(a.precip_mm_anual-a[f'mean_{start}_{end}']).where(a[f'count_{start}_{end}']==30)
        a[f'precip_zscore_{start}_{end}']=a[f'precip_anomaly_{start}_{end}']/a[f'std_{start}_{end}'].where(a[f'std_{start}_{end}']>0)
        a[f'precip_deficit_{start}_{end}']=(-a[f'precip_anomaly_{start}_{end}']).clip(lower=0)
        a[f'precip_excess_{start}_{end}']=a[f'precip_anomaly_{start}_{end}'].clip(lower=0)
    save(a,'h2__precip_anomaly__chirps_v2__ano_civil_candidatos.csv')
    write_json('catalog/validacao_chirps_rasters.json',info)

if __name__=='__main__':main()
