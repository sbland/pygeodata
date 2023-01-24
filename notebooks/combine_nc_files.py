import pandas as p
import numpy as np
from matplotlib import pyplot as plt
import os
import sys
import xarray as xr
# %%
FILE_DIR = sys.argv[-2]
OUT_DIR = sys.argv[-1]
print(f'Getting files from {FILE_DIR}')
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
print('Opening dataset')
files_list = os.listdir(FILE_DIR)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

for i, files in enumerate(chunks(sorted(files_list), 20)):
    loaded_files = [
            xr.open_dataset(
            f'{FILE_DIR}/{f}', engine="netcdf4", chunks=30
        ).where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True)
        .squeeze(['bottom_top', 'south_north', 'west_east'])[required_vars]
        for f in files
    ]


    ds_combined = xr.concat(loaded_files, 'Time', data_vars=required_vars)
    ds_combined.to_netcdf(f'{OUT_DIR}/out_combined_{i}.nc')
# %%
combined_files_list = os.listdir(OUT_DIR)
for i, file in enumerate(filter(lambda f :'.nc' in f, combined_files_list)):
    ds = xr.open_dataset(f'{OUT_DIR}/{file}')
    name = file.split('.')[0]
    ds.to_dataframe().to_csv(f'{OUT_DIR}/{name}.csv')

# %%
# print('Opening dataset')
# ds = xr.open_mfdataset(
#     f'{FILE_DIR}/*', concat_dim='Time', combine='nested', parallel=True, engine="netcdf4"
# ).where(lambda d: (d.bottom_top==0) & (d.south_north==0) & (d.west_east==0),drop=True
# )#.squeeze(['bottom_top', 'south_north', 'west_east'])# [required_vars]
# print('opened dataset')
# ds_f = ds.squeeze(['bottom_top', 'south_north', 'west_east'])[required_vars]
# # %%

# ds_f.to_netcdf(f'{OUT_DIR}/combined.nc')
# print('saved dataset')
# # %%
# ds_f.to_dataframe().to_csv(f'{OUT_DIR}/combined.csv')
# print(f'output saved to "{OUT_DIR}/combined.csv"')
# # %%