# ! python
# getDCWeather.py - Prints the weather for Cleveland Park, Washington, DC

# Import modules
import json, requests

# API key
APPID = '868c135ff7f42fa7e6688c7dba057746'

# Cleveland Park Coordinates
lat = '38.9346'
lon = '-77.0664'

# API Call
url = "https://api.openweathermap.org/data/2.5/onecall?lat=%s&lon=%s&appid=%s&units=imperial" % (lat, lon, APPID)

# Returns a response object
response = requests.get(url)

# Check for errors. If no exceptions are raised, the downloaded text is stored in response.text
response.raise_for_status()

# Uncomment to see the raw JSON text:
#print(response.text)

# Load JSON data into a Python object
weatherData = json.loads(response.text)
current = weatherData['current']

# Print current weather
print('The current weather for Cleveland Park, Washington, DC:')
print('Temperature: ' + str(current['temp']))
print('Feels like: ' + str(current['feels_like']))
print('Cloud Cover: ' + current['weather'][0]['description'])