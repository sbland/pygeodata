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
# %%
assert api_key is not None, "Set api key!"
# %%
def get_nasa_data(params, lon, lat, start, end, api_key=None,**kwargs):
    host="https://power.larc.nasa.gov"
    api_url= host + "/api/temporal/hourly/point"
    query = dict(
        parameters=','.join(params),
        community="AG",
        longitude=lon,
        latitude=lat,
        start=start,
        end=end,
        format=kwargs.get('format', 'json'),
        api_key=api_key,
        **kwargs,
    )

    response = requests.get(api_url, params=query)
    data = response.json()
    lon, lat, elevation = data['geometry']['coordinates']

    time_data = list(zip(*sorted(data['properties']['parameter'][params[0]].items(), key=lambda x: x[0])))[0]
    data = {k: list(zip(*list(sorted(data['properties']['parameter'][k].items(), key=lambda x: x[0]))))[1] for k in params}
    data['time_data'] = time_data

    df = pd.DataFrame(data)
    df = df.set_index('time_data')
    return df

# %%
new_data = get_nasa_data(['T2M'], '10', '22', '20101001', '20101002')
new_data
# %%
new_data.T2M.plot()
# %%
new_data.to_csv('tmp.csv')
# %%
