import requests
from datetime import date, datetime

# get current date
today = date.today()
today = str(today)

# format of date/time strings; assuming yyyy/mm/dd
date_format = "%Y-%m-%d"

today = datetime.strptime(today, date_format)

# get the list of races in the current year
url = 'http://ergast.com/api/f1/current.json'
response = requests.get(url)
jsonResponse = response.json()

parsedResponse = jsonResponse['MRData']['RaceTable']['Races']

round = 0

for race in parsedResponse:
    race_date = race['date']
    race_date = datetime.strptime(race_date, date_format)
    print('RACE DATE')
    print(race_date)
    print(type(race_date))
    
    if (race_date >= today):
        round = int(race['round'])
        break
        
if round == 0:
    reply = 'There are no more races scheduled for this F1 season'
else:
    race = parsedResponse[round - 1]
    raceName = race['raceName']
    raceDate = race['date']
    raceDate = datetime.strptime(raceDate, date_format)
    raceDate = raceDate.strftime("%B %d, %Y")
    circuitName = race['Circuit']['circuitName']
    raceCity = race['Circuit']['Location']['locality']
    raceCountry = race['Circuit']['Location']['country']
    # example reply
    # The next race will be the Portuguese Grand Prix, held on May 2, 2021 at the Autódromo Internacional do Algarve in Portimão, Portugal.
    reply = """The next race will be the {}, held on {} at the {} in {} ({})""".format(raceName, raceDate, circuitName, raceCity, raceCountry)

print(reply)