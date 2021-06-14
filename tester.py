import requests
import utils as utils
from difflib import SequenceMatcher

constructor = 'Ferrari'

year_slot = "2014"

if year_slot == "None":
    year = 'current'
    when = 'are'
else:
    year = int(year_slot)
    when = 'were'

url = f'http://ergast.com/api/f1/{year}/constructors.json'
response = requests.get(url)
jsonResponse = response.json()

parsedResponse = jsonResponse['MRData']['ConstructorTable']['Constructors']

best_match = utils.searchConstructor(constructor, parsedResponse)

print(best_match)

url = f'http://ergast.com/api/f1/constructors/{best_match}.json'
response = requests.get(url)
jsonResponse = response.json()

constructor_name = jsonResponse['MRData']['ConstructorTable']['Constructors'][0]['name']

url = f'http://ergast.com/api/f1/{year}/driverStandings.json'
response = requests.get(url)
jsonResponse = response.json()

all_drivers = jsonResponse['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
constructor_drivers = []

for entry in all_drivers:
    tmp_constructor = entry['Constructors'][0]['constructorId']
    if tmp_constructor == best_match:
        full_name = entry['Driver']['givenName'] + ' ' + entry['Driver']['familyName']
        constructor_drivers.append(full_name)
        
reply = """The {} drivers for the {} F1 season {}""".format(constructor_name, year, when)

for i in range(0, len(constructor_drivers)):
    if i == (len(constructor_drivers) - 1):
        reply = reply + ' and ' + constructor_drivers[i] + '.'
    elif i == 0:
        reply = reply + ' ' + constructor_drivers[i]
    else:
        reply = reply + ', ' + constructor_drivers[i]

print(reply)