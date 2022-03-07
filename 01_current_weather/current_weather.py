# ! python
# current_weather.py
'''
current_weather.py retrieves the current weather conditions at the location of
the user's IP address. The data is retrived with the Open Weather Map API.
'''

# Import modules
import json
import requests
import os
import geocoder
from dotenv import load_dotenv

# Retrieve credentials and set environment variables
load_dotenv()
APPID = os.environ.get('openweather_key')


# Define function to get location
def user_location():
    '''
    Return the user's latitude and longitude coordinates based on their
    IP address.
    '''
    g = geocoder.ip('me')
    coordinates = list(g.latlng)
    lat, lon = coordinates
    city = g.city
    state = g.state
    return lat, lon, city, state


# Define function to print current weather conditions.
def output_weather():
    '''Prints the current weather conditions for the user's location.'''
    if state == 'Washington, D.C.':
        print(f'The current weather for {state}:')
    else:
        print(f'The current weather for {city}, {state}:')

    print('Temperature: ' + str(current['temp']))
    print('Feels like: ' + str(current['feels_like']))
    print('Cloud Cover: ' + current['weather'][0]['description'].title())

# Retrieve User's Coordinates
lat, lon, city, state = user_location()

# API Call
url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={APPID}&units=imperial"

# Returns a response object
response = requests.get(url)

# Check for errors.
# If no exceptions are raised, the downloaded text is stored in response.text
response.raise_for_status()

# Load JSON data into a Python object
weatherData = json.loads(response.text)
current = weatherData['current']

# Print current weather
print(output_weather())