"""Access NASA climate data.
https://power.larc.nasa.gov/api/pages/?urls.primaryName=Hourly
https://power.larc.nasa.gov/docs/services/api/temporal/hourly/#request-structure

Parameter info: https://power.larc.nasa.gov/#resources
Pick a parameter from the dropdown and make note of it's abbreviation
"""
# %%
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import requests

import geopandas as gpd
import cartopy.crs as ccrs
# %%
assert api_key is not None, "Set api key!"

# %%
def get_nasa_data(params, lon, lat, start, end, api_key=None,**kwargs):
    host="https://power.larc.nasa.gov"
    api_url= host + "/api/temporal/hourly/point"
    format = kwargs.pop('format', 'json')
    query = dict(
        parameters=','.join(params),
        community="AG",
        longitude=lon,
        latitude=lat,
        start=start,
        end=end,
        format=format,
        header=False,
        api_key=api_key,
        **kwargs,
    )

    response = requests.get(api_url, params=query)
    if format == "csv":
        decoded_content = response.content.decode('utf-8')
        cr = list(csv.reader(decoded_content.splitlines(), delimiter=','))
        df= pd.DataFrame(cr[1:], columns=cr[0])
        return df, None
    else:
        data = response.json()
        lon, lat, elevation = data['geometry']['coordinates']

        time_data = list(zip(*sorted(data['properties']['parameter'][params[0]].items(), key=lambda x: x[0])))[0]
        data = {k: list(zip(*list(sorted(data['properties']['parameter'][k].items(), key=lambda x: x[0]))))[1] for k in params}
        data['time_data'] = time_data

        df = pd.DataFrame(data)
        df = df.set_index('time_data')
        return df, elevation

# %%
import csv

example_data_csv, ele = get_nasa_data(['T2M'], 20,10, '20101010', '20101011', api_key=api_key, format="csv")
example_data_csv.head()
# %%
example_data_from_json, ele = get_nasa_data(['T2M'], 20,10, '20101010', '20101011', api_key=api_key, format="json")
example_data_from_json.head()

# %%
example_data_from_json.T2M.plot()
# %%
# example_data_from_json.to_csv('tmp.csv')
# %%
