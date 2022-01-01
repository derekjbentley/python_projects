# ! python
# getCOVIDdataV2.py - Gets latest COVID-19 hisorical daily values for the US by state from The COVID Tracking Project

# Import modules
import json
import requests
import pandas as pd
import pygsheets
import time

# Print Timestamp
timestamp = time.strftime("%Y-%m-%d %H:%M", time.gmtime())
print('running...')
print(f'timestamp: {timestamp}')

# API Call
url = "https://covidtracking.com/api/v1/states/daily.json"

# Returns a response object
response = requests.get(url)
print('Retreiving data...')

# Check for errors. If no exceptions are raised, the downloaded text is stored in response.text
response.raise_for_status()

# Uncomment to see the raw JSON text:
#print(response.text)

# Load JSON data into a Python object
covidData = json.loads(response.text)

# Create DataFrame with JSON data
df = pd.DataFrame(covidData)

# Export Full DataFrame to CSV
print('Writing to CSV...')
df.to_csv(r'C:\Users\derek\snek\COVID_data.csv', index=False , header=True)

# Drop some columns
print('Dropping columns for Sheets...')
df = df.drop(['dataQualityGrade','lastUpdateEt', 'dateModified', 'checkTimeEt','dateChecked',
 'hash', 'commercialScore', 'score', 'grade', 'negativeRegularScore', 'negativeScore', 'positiveScore', 'fips', 
 'deathConfirmed', 'deathProbable', 'negativeTestsAntibody', 'negativeTestsPeopleAntibody', 'negativeTestsViral', 
 'onVentilatorCumulative', 'onVentilatorCurrently', 'pending', 'posNeg', 'positiveCasesViral', 'positiveScore', 
 'positiveTestsAntibody', 'positiveTestsAntigen', 'positiveTestsPeopleAntibody', 'positiveTestsPeopleAntigen', 
 'positiveTestsViral', 'probableCases', 'totalTestEncountersViral', 'totalTestResultsSource', 'totalTestsAntibody', 
 'totalTestsAntigen', 'totalTestsPeopleAntibody', 'totalTestsPeopleAntigen', 'totalTestsPeopleViral', 'totalTestsViral',
 'hospitalizedCumulative', 'hospitalizedCurrently', 'hospitalizedIncrease', 'inIcuCumulative', 'inIcuCurrently'], axis = 1)

# Write DataFrame to Google Sheet
print('Writing to Sheets...')
service = pygsheets.authorize('credentials.json')
workbook = service.open('COVIDdata')
sheet = workbook[0]
sheet.set_dataframe(df, (1,1), fit=False)
print('Done')