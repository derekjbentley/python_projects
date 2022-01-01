# %% [markdown]
# ### get_weather
# 
# A script to query the openweather API to collect and transform the data for data visualization.

# %%
## import modules
import requests
import json
import pandas as pd
import pytz
import pygsheets
import os

from dotenv import load_dotenv
from functools import reduce

# %%
## Retrieve credentials and set environment variables
load_dotenv()
APPID = os.environ.get('openweather_key')

# %%
# Cleveland Park Coordinates
lat = '38.9346'
lon = '-77.0664'

# %%
units = 'imperial'
# units = ['standard', 'metric', 'imperial']

# %%
url = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={APPID}&units={units}'

# %%
# Returns a response object
response = requests.get(url)

# %%
# Check for errors. If no exceptions are raised, the downloaded text is stored in response.text
response.raise_for_status()

# %%
# Load JSON data into a Python object
weatherdata = json.loads(response.text)

# %%
weather_data = pd.DataFrame()

# %%
## Use orient index to avoid ValueError: arrays must all be same length
weather_data = weather_data.from_dict(weatherdata, orient='index')

# %%
weather_data = weather_data.transpose()

# %% [markdown]
# ### Transform daily data

# %%
## Create a DataFrame for the daily data
daily_df = pd.DataFrame(weather_data.daily[0])

# %%
## Turn columns of dicts into DataFrames
temp_df = pd.DataFrame(list(daily_df.temp))
temp_df.columns = [str(col) + '_temp' for col in temp_df.columns]

# %%
feels_df = pd.DataFrame(list(daily_df.feels_like))
feels_df.columns = [str(col) + '_feel' for col in feels_df.columns]

# %%
weather_df = pd.DataFrame(list(daily_df.weather))
weather_list = list(weather_df[0])
weather_df = pd.DataFrame(weather_list)

# %%
merge_list = [daily_df, temp_df, feels_df, weather_df]

# %%
## merge the list of DataFrames
merge_df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), merge_list)

# %%
## Drop columns
merge_df = merge_df.drop(['temp', 'feels_like', 'weather'], axis=1)

# %%
## Convert datetime columns from unix to standard time
merge_df[['dt', 'sunrise', 'sunset']] = merge_df[['dt', 'sunrise', 'sunset']].apply(pd.to_datetime, unit='s')
merge_df = merge_df.rename(columns={'dt': 'date_time'})

# %%
## Make datetime objects offset aware and set time to 'Eastern/US'
utc_tz = pytz.utc
eastern_tz = pytz.timezone('US/Eastern')

merge_df['date_time'] = merge_df['date_time'].dt.tz_localize(utc_tz)
merge_df['sunrise'] = merge_df['sunrise'].dt.tz_localize(utc_tz)
merge_df['sunset'] = merge_df['sunset'].dt.tz_localize(utc_tz)

merge_df['date_time'] = merge_df['date_time'].dt.tz_convert(eastern_tz)
merge_df['sunrise'] = merge_df['sunrise'].dt.tz_convert(eastern_tz)
merge_df['sunset'] = merge_df['sunset'].dt.tz_convert(eastern_tz)

# %%
## Transform colums containing _temp or _feel with pd.melt 
temps = merge_df[['date_time','day_temp', 'min_temp', 'max_temp', 'night_temp', 'eve_temp', 'morn_temp']]
feels = merge_df[['date_time', 'day_feel', 'night_feel', 'eve_feel', 'morn_feel']]

temps = pd.melt(temps, id_vars='date_time', value_vars=['day_temp', 'min_temp', 'max_temp', 'night_temp', 'eve_temp', 'morn_temp'])
feels = pd.melt(feels, id_vars='date_time', value_vars=['day_feel', 'night_feel', 'eve_feel', 'morn_feel'])

temps = temps.rename(columns={'variable': 'temp', 'value': 'temp_value'})
feels = feels.rename(columns={'variable': 'feel', 'value': 'feel_value'})

merge_df = pd.merge(merge_df, temps, left_on='date_time', right_on='date_time')
merge_df = pd.merge(merge_df, feels, left_on='date_time', right_on='date_time')

merge_df = merge_df.drop(['day_feel', 'night_feel', 'eve_feel', 'morn_feel', 'day_temp', 'min_temp', 'max_temp', 'night_temp', 'eve_temp', 'morn_temp'], axis=1)

# %% [markdown]
# ### Transform hourly data

# %%
hourly_df = pd.DataFrame(weather_data.hourly[0])

# %%
weather_df = pd.DataFrame(list(hourly_df.weather))
weather_list = list(weather_df[0])
weather_df = pd.DataFrame(weather_list)

# %%
hourly_df = pd.merge(hourly_df, weather_df, left_index=True, right_index=True)
hourly_df = hourly_df.drop(['weather'], axis=1)

# %%
hourly_df['dt'] = pd.to_datetime(hourly_df['dt'], unit='s')
hourly_df['dt'] = hourly_df['dt'].dt.tz_localize(utc_tz)
hourly_df['dt'] = hourly_df['dt'].dt.tz_convert(eastern_tz)
hourly_df = hourly_df.rename(columns={'dt': 'date_time'})

# %%
## Extract the values from the non-null rain dicts
rain_df = hourly_df[['date_time', 'rain']]
rain_df = rain_df[rain_df.rain.notnull()]
rain_df = rain_df.reset_index(drop=True)
rain_srs = [d.get('1h') for d in rain_df.rain]
rain_df['precipitation'] = rain_srs

# %%
hourly_df = pd.merge(left=hourly_df, right=rain_df, how='left',left_on='date_time', right_on='date_time')
hourly_df = hourly_df.drop(['rain_x', 'rain_y'], axis=1)

# %%
## Write data to Google Sheets
print('Writing to Sheets...')
service = pygsheets.authorize(client_secret='client_secret.json')
workbook = service.open('seven_day_forecast')
sheet1 = workbook[0]
sheet1.set_dataframe(merge_df, (1,1), fit=False)
sheet2 = workbook[1]
sheet2.set_dataframe(hourly_df, (1,1), fit=False)