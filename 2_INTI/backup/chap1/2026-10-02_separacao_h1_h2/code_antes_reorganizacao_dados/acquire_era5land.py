"""Prepare CDS request without reading or storing secrets in the repository.

Requires the user's CDS account, dataset licence acceptance and configured cdsapi.
Run only after installing cdsapi and configuring ~/.cdsapirc externally.
"""
import argparse,json
from data_common import DATA,write_json

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--download',action='store_true');args=p.parse_args()
    request={'product_type':['monthly_averaged_reanalysis'],'variable':['2m_temperature'],'year':[str(y) for y in range(1981,2026)],'month':[f'{m:02d}' for m in range(1,13)],'time':['00:00'],'data_format':'netcdf','download_format':'unarchived','area':[-7,-62,-19,-50]}
    write_json('catalog/era5land_request_candidate.json',{'dataset':'reanalysis-era5-land-monthly-means','request':request,'status':'REQUER_CONTA_CDS_E_ACEITE_LICENCA','scope':'monthly mean cannot produce daily extreme heat days'})
    if args.download:
        import cdsapi
        target=DATA/'raw/raster/era5land/temperature_1981_2025.nc';target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():raise FileExistsError(target)
        cdsapi.Client().retrieve('reanalysis-era5-land-monthly-means',request,str(target))
