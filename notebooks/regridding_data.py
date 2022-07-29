# %%
# Example of regridding a netcdf file to another grid.# %%
import xarray as xr
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cf
from copy import copy
import math
import itertools
import numpy as np
import itertools
import matplotlib.patches as mpatches

import matplotlib.ticker as mticker
import cartopy.crs as ccrs

from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

# %%
ds = xr.open_dataset('data/Wheat.Winter.crop.calendar.nc')
ds_wrf = xr.open_dataset('data/wrfchem_demo_out_01_10_00.nc')

# %%
# China dataset extents
DS_WRF_EXTENTS = [105, 125, 25, 45]
DS_WRF_EXTENTS_Z1 = [110, 125, 30, 40]
# %%
# Plot Crop calandar grid
plt.figure(figsize=(12,12))
ax = plt.axes(projection=ccrs.Mercator())
ax.coastlines()

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

gl.xlabels_top = False
gl.ylabels_left = False
# gl.xlines = False
gl.xlocator = mticker.FixedLocator(ds.coords['longitude'].values)
gl.ylocator = mticker.FixedLocator(ds.coords['latitude'].values)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
# TODO: Set this to china
ax.set_extent(DS_WRF_EXTENTS_Z1, ccrs.PlateCarree())

plt.show()


# %%
# Get Wrfchem boundaries
rects = []
for xi, yi in itertools.product(list(range(48)),list(range(48))):
    lat = ds_wrf.coords['XLAT_V'][0][xi, yi].values
    long = ds_wrf.coords['XLONG_V'][0][xi, yi].values
    latx = ds_wrf.coords['XLAT_U'][0][xi, yi].values
    longx = ds_wrf.coords['XLONG_U'][0][xi, yi].values
    height = (latx - lat) * 2
    width = (long - longx) * 2
    rect = mpatches.Rectangle(xy=[long, lat], width=width, height=height,
                                edgecolor='red',
                                facecolor='none',
                                alpha=0.9,
                                linewidth=1,
                                transform=ccrs.PlateCarree())
    rects.append(rect)
    # ax.add_patch(rect)
# %%
# Plot wrfchem boundaries over crop data grid
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.Mercator())
for rect in rects:
    ax.add_patch(copy(rect))
ax.coastlines()

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

gl.top_labels = False
gl.left_labels = False
# NOTE: values offset to show boundary not centerpoint
gl.xlocator = mticker.FixedLocator(ds.coords['longitude'].values + 0.25)
gl.ylocator = mticker.FixedLocator(ds.coords['latitude'].values + 0.25)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
ax.set_extent(DS_WRF_EXTENTS, ccrs.PlateCarree())

plt.show()

# %%
# Plot with harvest data
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.PlateCarree())
for rect in rects:
    ax.add_patch(copy(rect))
ax.coastlines()

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

gl.top_labels = False
gl.left_labels = False
# NOTE: values offset to show boundary not centerpoint
gl.xlocator = mticker.FixedLocator(ds.coords['longitude'].values + 0.25)
gl.ylocator = mticker.FixedLocator(ds.coords['latitude'].values + 0.25)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
ax.set_extent(DS_WRF_EXTENTS, ccrs.PlateCarree())
ds['harvest'].plot(ax=ax)
plt.show()

# %%
# Get centroids
a_points = list(itertools.product(enumerate(ds.coords['longitude'].values.tolist()),enumerate(ds.coords['latitude'].values.tolist())))
a_points = [(x, y, lon, lat) for (x, lon), (y, lat) in a_points]
b_points = [
    (xi, yi, ds_wrf.coords['XLONG_V'][0][xi, yi].values.tolist(), ds_wrf.coords['XLAT_U'][0][xi, yi].values.tolist()) for xi, yi in itertools.product(list(range(49)),list(range(49)))
]

a_points_filtered = [(x, y, lon, lat) for x, y, lon, lat in a_points if (105 < lon < 125) and (25 < lat < 45)]
# %%
# Find nearest crop data points to wrfchem centroids
nearest_points = np.full((49,49, 4), None)
for xi, yi, lon, lat, in b_points:
    d = 999999999999
    nearp = None
    for xj, yj, lon_a, lat_a in a_points_filtered:
        dj = math.hypot(lon_a - lon, lat_a - lat)
        if dj < d:
            d = dj
            nearp= (xj, yj, lon_a, lat_a)
        else:
            continue
    nearest_points[xi, yi] = nearp


# %%
# Plot nearest neighbour results
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.PlateCarree())
for rect in rects:
    ax.add_patch(copy(rect))
ax.coastlines()

gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=False,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')

gl.top_labels = False
gl.left_labels = False
gl.xlocator = mticker.FixedLocator(ds.coords['longitude'].values)
gl.ylocator = mticker.FixedLocator(ds.coords['latitude'].values)
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
ax.set_extent(DS_WRF_EXTENTS, ccrs.PlateCarree())
for xi, yi, lon, lat, in b_points:
    [xj, yj, lon_a, lat_a] = nearest_points[xi, yi]
    ax.plot([lon, lon_a], [lat, lat_a])

plt.show()
# %%
# Zoom in on nearest neighbour result plot
plt.figure(figsize=(20,20))
ax = plt.axes(projection=ccrs.PlateCarree())
for xi, yi, lon, lat, in b_points:
    [xj, yj, lon_a, lat_a] = nearest_points[xi, yi]
    ax.plot([lon, lon_a], [lat, lat_a])
ax.scatter(
    [lon for xi, yi, lon, lat in b_points],
    [lat for xi, yi, lon, lat in b_points],
)
ax.scatter(
    [lon for x, y, lon, lat in a_points_filtered],
    [lat for x, y, lon, lat in a_points_filtered],
)
ax.coastlines()
ax.set_extent([115, 118, 30, 40], ccrs.PlateCarree())

plt.show()
# %%
# Get additional data from nearest neighbour
x, y, lon, lat = nearest_points[0, 0]
print(x, y, lon, lat)
ds['harvest'][y, x]
# %%
# TODO: Export a netcdf file of crop dates and land cover gridded to wrfchem grid