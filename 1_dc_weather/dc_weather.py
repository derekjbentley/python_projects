# ! python
# dc_weather.py - Prints the weather for Cleveland Park, Washington, DC

## Import modules
import json
import requests
import os
from dotenv import load_dotenv

## Retrieve credentials and set environment variables
load_dotenv()
APPID = os.environ.get('openweather_key')

## Cleveland Park Coordinates
lat = '38.9346'
lon = '-77.0664'

## API Call
url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={APPID}&units=imperial"

## Returns a response object
response = requests.get(url)

## Check for errors. If no exceptions are raised, the downloaded text is stored in response.text
response.raise_for_status()

## Load JSON data into a Python object
weatherData = json.loads(response.text)
current = weatherData['current']

## Print current weather
print('The current weather for Cleveland Park, Washington, DC:')
print('Temperature: ' + str(current['temp']))
print('Feels like: ' + str(current['feels_like']))
print('Cloud Cover: ' + current['weather'][0]['description'].title())