# %%
import pandas as p

import numpy as np
from matplotlib import pyplot as plt
import os
import sys
import xarray as xr
from datetime import datetime
# %%
FILE_DIR = 'data/large_netcdf'
OUT_DIR = 'tmp_combine'
os.makedirs(OUT_DIR, exist_ok=True)
# %%
required_vars = [
    'td_2m',
    'pres',
    'SWDOWN',
    'RAINNC',
    'rh',
    'wspeed',
    'o3',
    'HFX_FORCE',
    'SNOWH',
]
required_coordinates= [
    'XTIME',
    'XLAT',
    'XLONG',
 ]
# %%
# MULTI APPROACH
ts = datetime.now()
print('Opening dataset')
ds = xr.open_mfdataset(
    f'{FILE_DIR}/*', concat_dim='Time', combine='nested', parallel=True, engine="netcdf4", chunks='auto'
)[required_vars]
ds.to_netcdf(f'{OUT_DIR}/outa.nc')
te = datetime.now()
print(te - ts)
ds
# %%

# 1 FILE AT A TIME
ts = datetime.now()
print('Opening dataset')
dsa = xr.open_dataset(
    f'{FILE_DIR}/01.nc', engine="netcdf4", chunks=30
)
dsb = xr.open_dataset(
    f'{FILE_DIR}/02.nc', engine="netcdf4", chunks=30
)
ds = xr.concat([dsa, dsb], 'Time', data_vars=required_vars)[required_vars]
ds.to_netcdf(f'{OUT_DIR}/outb.nc')
te = datetime.now()
print(te - ts)
ds

# %%
# ==== FILTERs
# %%
# MULTI APPROACH
ts = datetime.now()
print('Opening dataset')
ds = xr.open_mfdataset(
    f'{FILE_DIR}/*', concat_dim='Time', combine='nested', parallel=True, engine="netcdf4", chunks='auto'
).where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True)[required_vars]
ds.to_netcdf(f'{OUT_DIR}/outa.nc')
te = datetime.now()
print(te - ts)
ds
# %%

# 1 FILE AT A TIME
ts = datetime.now()
print('Opening dataset')
dsa = xr.open_dataset(
    f'{FILE_DIR}/01.nc', engine="netcdf4", chunks='auto'
).where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True).squeeze(['bottom_top', 'south_north', 'west_east'])[required_vars]
dsb = xr.open_dataset(
    f'{FILE_DIR}/02.nc', engine="netcdf4", chunks='auto'
).where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True).squeeze(['bottom_top', 'south_north', 'west_east'])[required_vars]
ds = xr.concat([dsa, dsb], 'Time', data_vars=required_vars)
ds.to_netcdf(f'{OUT_DIR}/outb.nc')
te = datetime.now()
print(te - ts)
ds

# %%
# Check merging
# dsa.Time,dsb.Time
ds = xr.concat([dsa, dsb], 'Time', data_vars=required_vars)[required_vars]
ds
# %%
# Check opening
ds  = xr.open_dataset(
    f'{OUT_DIR}/outb.nc', engine="netcdf4", chunks='auto'
)
ds
# ====================================================
# %%
# ==== FILTERs
ds_where = ds.where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True)
#.squeeze(['bottom_top', 'south_north', 'west_east'])# [required_vars]
print('opened dataset')
ds_f = ds_where.squeeze(['bottom_top', 'south_north', 'west_east'])[required_vars]
# %%

ds_f.to_netcdf(f'{OUT_DIR}/combined.nc')
print('saved dataset')
# %%
ds_f.to_dataframe().to_csv(f'{OUT_DIR}/combined.csv')
print(f'output saved to "{OUT_DIR}/combined.csv"')
# %%