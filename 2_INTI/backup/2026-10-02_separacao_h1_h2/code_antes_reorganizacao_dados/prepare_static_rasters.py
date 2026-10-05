"""Municipal candidates from original GAEZ and Copernicus rasters.

GAEZ uses pixel centres and cos(latitude) weights. DEM means use native pixels;
no slope or ruggedness is fabricated from an elevation mean.
"""
import numpy as np,pandas as pd,geopandas as gpd,rasterio
from rasterio.mask import mask
from data_common import DATA,write_json
from prepare_h1_h2 import save

def main():
    municipalities=gpd.read_file('zip://'+str(DATA/'raw/vector/ibge/MT_Municipios_2024.zip')).to_crs(4326)
    result=[];metadata=[]
    for p in sorted((DATA/'raw/raster/gaez_v4_6190').glob('*.tif')):
        with rasterio.open(p) as src:
            metadata.append({'arquivo':str(p.relative_to(DATA)),'crs':str(src.crs),'resolution':list(src.res),'bbox':list(src.bounds),'nodata':src.nodata,'bands':src.count,'dtype':src.dtypes[0]})
            for r in municipalities.itertuples():
                a,tr=mask(src,[r.geometry],crop=True,filled=False)
                a=a[0];lat=tr.f+(np.arange(a.shape[0])+.5)*tr.e
                weights=np.broadcast_to(np.cos(np.deg2rad(lat))[:,None],a.shape)
                valid=~np.ma.getmaskarray(a)
                val=np.average(a.data[valid],weights=weights[valid]) if valid.any() else np.nan
                result.append({'codigo_ibge':r.CD_MUN,'municipio':r.NM_MUN,'variavel_raster':p.stem,'valor_medio':val,'n_pixels_validos':int(valid.sum()),'nivel_insumo':'alto' if 'Hr0' in p.stem else 'baixo','periodo_climatico':'1961-1990','regime':'sequeiro','unidade':'indice 0-10000' if p.stem.startswith('sx') else 'kg materia seca/ha'})
    save(pd.DataFrame(result),'h1__suitability_yield__gaez_v4_6190__candidatos.csv')
    # Native COG tile statistics; municipal membership tested per pixel.
    sums=np.zeros(len(municipalities));counts=np.zeros(len(municipalities));mins=np.full(len(municipalities),np.inf);maxs=np.full(len(municipalities),-np.inf)
    from shapely.geometry import box
    for p in sorted((DATA/'raw/raster/copdem90').glob('*.tif')):
        with rasterio.open(p) as src:
            metadata.append({'arquivo':str(p.relative_to(DATA)),'crs':str(src.crs),'resolution':list(src.res),'bbox':list(src.bounds),'nodata':src.nodata,'bands':src.count,'dtype':src.dtypes[0]})
            extent=box(*src.bounds)
            for i,r in enumerate(municipalities.itertuples()):
                if not r.geometry.intersects(extent):continue
                a,_=mask(src,[r.geometry],crop=True,filled=False);v=a.compressed()
                if not len(v):continue
                sums[i]+=v.sum(dtype='float64');counts[i]+=len(v);mins[i]=min(mins[i],v.min());maxs[i]=max(maxs[i],v.max())
    d=pd.DataFrame({'codigo_ibge':municipalities.CD_MUN,'municipio':municipalities.NM_MUN,'elevation_mean_m':np.divide(sums,counts,out=np.full(sums.shape,np.nan),where=counts>0),'elevation_min_m':np.where(counts>0,mins,np.nan),'elevation_max_m':np.where(counts>0,maxs,np.nan),'n_pixels':counts.astype(int)})
    save(d,'topography__copdem90__municipio_candidato.csv')
    write_json('catalog/validacao_rasters_estaticos.json',metadata)

if __name__=='__main__':main()
