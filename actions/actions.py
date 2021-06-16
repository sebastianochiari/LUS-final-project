# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from logging import addLevelName
import requests
import datetime
import random

from utils import searchConstructor, searchDriver, searchDriverDescription, searchGrandPrix

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import AllSlotsReset, Form, SlotSet

with open('data/F1jokes.txt', 'r') as f:
    jokes = f.read().splitlines()

class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"
    
    def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]

class ActionReplyWithJoke(Action):
    def name(self) -> Text:
        return 'action_reply_with_joke'

    def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        
        jokeNumber = random.randint(0, len(jokes) - 1)
        reply = jokes[jokeNumber]
        dispatcher.utter_message(reply)
        
        return []

class ActionSearchDriverByConstructor(Action):
    def name(self) -> Text:
        return "action_search_drivers_by_constructor"
    
    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

        print('Executing action_search_drivers_by_constructor')

        constructor = tracker.get_slot('constructor')

        print('Constructor: ' + constructor)

        year_slot = tracker.get_slot('year')

        if year_slot is None:
            year = 'current'
            when = 'are'
        else:
            year = year_slot
            when = 'were'

        print('Year: ' + year)

        url = f'http://ergast.com/api/f1/{year}/constructors.json'
        response = requests.get(url)
        jsonResponse = response.json()

        parsedResponse = jsonResponse['MRData']['ConstructorTable']['Constructors']

        best_match, confidence = searchConstructor(constructor, parsedResponse)

        print(best_match)
        print(confidence)

        if confidence >= 0.5:
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
            
            dispatcher.utter_message(reply)

            return [SlotSet('constructor', best_match)]
        
        else:
            dispatcher.utter_message('It seems there is no constructor team corresponding to your input.\nTry again.')
            return [SlotSet('constructor', None)]
    
class ValidateRaceResultForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_race_result_form"

    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text], 
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker", 
        domain: "DomainDict"
    ) -> Optional[List[Text]]:
        outcome = tracker.get_slot("driver_or_ranking")
        driver = tracker.get_slot("driver")
        if (outcome == "/driver") and (driver is None):
            print('Sono dentro a IF driver')
            return ['driver'] + slots_mapped_in_domain
        return slots_mapped_in_domain

    async def extract_driver_or_ranking(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict"
    ) -> Dict[Text, Any]:    
        intent = tracker.get_intent_of_latest_message()
        if intent == '/driver':
            return {'driver_or_ranking': 'driver'}
        elif intent == '/ranking':
            return {'driver_or_ranking': 'ranking'}

    def validate_year(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate year value."""

        year = int(slot_value)
        # log print
        print(f'Year given: {year}')
        # retrieve current year
        currentDateTime = datetime.datetime.now()
        current_year = int((currentDateTime.date()).strftime("%Y"))

        if 1950 <= year <= current_year:
            # validation succeeded, set the value of the "year" slot to value
            print('Year: ' + str(year))
            return {"year": slot_value}
        else:
            # validation failed, set this slot to None so that the
            # user will be asked for the slot again
            dispatcher.utter_message('Something went wrong with your input year.')
            return {"year": None}
    
    def validate_circuit(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate circuit value."""
        # if the name is super short, it might be wrong
        print(f"Circuit name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 3:
            dispatcher.utter_message(text=f"That's a very short circuit name. I'm assuming you mis-spelled.")
            return {"circuit": None}
        else:
            print('Circuit: ' + slot_value)
            return {"circuit": slot_value}
    
    def validate_driver(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate driver value."""
        # if the name is super short, it might be wrong
        print(f"Driver name given = {slot_value} length = {len(slot_value)}")
        if len(slot_value) <= 3:
            dispatcher.utter_message(text=f"That's a very short driver name. I'm assuming you mis-spelled.")
            return {"driver": None}
        else:
            print('Driver: ' + slot_value)
            return {"driver": slot_value}

class SearchRaceResult(Action):
    def name(self) -> Text:
        return 'action_search_race_result'
    
    async def run(self, dispatcher: "CollectingDispatcher", 
            tracker: Tracker,
            domain: "DomainDict") -> List[Dict[Text, Any]]:

        year = tracker.get_slot('year')
        circuit = tracker.get_slot('circuit')
        outcome = tracker.get_slot('driver_or_ranking')
        driver = tracker.get_slot('driver')

        # get all the races from the year
        url = f'http://ergast.com/api/f1/{year}.json'
        response = requests.get(url)
        jsonResponse = response.json()

        race_schedule = jsonResponse['MRData']['RaceTable']['Races']

        best_match, confidence, race_info = searchGrandPrix(circuit, race_schedule)

        print(best_match)
        print(confidence)
        print(race_info)

        if confidence < 0.6:
            print('Race not found for given year')
            # to be changed in dispatcher.utter_message('text')
            dispatcher.utter_message(f'I was not able to find the specified race during the {year} F1 season. May I suggest to try again?')
            # add reset slots
            return [SlotSet('year', None), SlotSet('circuit', None), SlotSet('driver_or_ranking', None), SlotSet('driver', None)]
        else:
            print('Race found for the given year')

            url = f'http://ergast.com/api/f1/{year}/{best_match}/results.json'
            response = requests.get(url)
            jsonResponse = response.json()

            race = jsonResponse['MRData']['RaceTable']['Races'][0]

            raceName = race['raceName']

            standings = race['Results']

            if outcome == '/ranking':
                print('Ranking request')

                podium = []

                for i in range(0, 3):
                    tmp_driver = []
                    fullName = standings[i]['Driver']['givenName'] + ' ' + standings[i]['Driver']['familyName']
                    tmp_driver.append(fullName)
                    team = standings[i]['Constructor']['name']
                    tmp_driver.append(team)
                    podium.append(tmp_driver)

                # example message
                # {Sergio Perez}, driving for {RedBull}, won the {2021} {Arzebaijan Gran Prix}.
                # In second and third place came {Sebastian Vettel}, {Aston Martin}, and {Pierre Gasly}, {Alpha Tauri}.

                reply = """{}, driving for {}, won the {} {}.\nIn second and third place came {}, {}, and {}, {}.""".format((podium[0])[0], podium[0][1],
                    year, raceName, podium[1][0], podium[1][1], podium[2][0], podium[2][1])

                dispatcher.utter_message(reply)

                return [SlotSet('year', year), SlotSet('circuit', raceName), SlotSet('driver_or_ranking', outcome), SlotSet('driver', None)]

            if outcome == '/driver':
                print('Driver request')

                url = f'http://ergast.com/api/f1/{year}/drivers.json'
                response = requests.get(url)
                jsonResponse = response.json()

                driversList = jsonResponse['MRData']['DriverTable']['Drivers']

                driverID, driverConfidence = searchDriver(driver, driversList)

                print(driverID)
                print(driverConfidence)

                if driverConfidence < 0.4:
                    print('Driver not found for given race')
                    # to be changed in dispatcher.utter_message('text')
                    dispatcher.utter_message(f'I was not able to find the driver you specified racing during the {year} {race_info[0]}. May I suggest to try again?')
                    # add reset slots
                    return [SlotSet('year', None), SlotSet('circuit', None), SlotSet('driver_or_ranking', None), SlotSet('driver', None)]
                else:
                    print('Driver found')

                    url = f'http://ergast.com/api/f1/{year}/{best_match}/drivers/{driverID}/results.json'
                    response = requests.get(url)
                    jsonResponse = response.json()

                    jsonDriver = jsonResponse['MRData']['RaceTable']['Races'][0]['Results'][0]

                    driver_name = jsonDriver['Driver']['givenName'] + ' ' + jsonDriver['Driver']['familyName']
                    team = jsonDriver['Constructor']['name']
                    position = jsonDriver['position']
                    grid = jsonDriver['grid']
                    status = jsonDriver['status']

                    # example message
                    # {Ferrari} driver {Charles Leclerc} finished in {4}th place the {2021} {Arzebaijan Gran Prix}, after starting from the {pole} position.
                    # {Astron Martin} driver {Lance Stroll} didn't finish the {2021} {Arzebaijan Gran Prix}, after starting from the {19}th position, due to an {accident}.

                    reply = """{} driver {} finished in position {} the {} {}, after starting from position {}.""".format(team, driver_name, position, year, raceName, grid)

                    dispatcher.utter_message(reply)

                    return [SlotSet('year', year), SlotSet('circuit', raceName), SlotSet('driver_or_ranking', outcome), SlotSet('driver', driverID)]

class ActionSearchWinnerByYear(Action):
    def name(self) -> Text:
        return 'action_search_winner_by_year'
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        year = tracker.get_slot('year')
        url = f'http://ergast.com/api/f1/{year}/driverStandings.json'
        response = requests.get(url)
        jsonResponse = response.json()
        
        parsedResponse = jsonResponse['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings'][0]
        
        points = parsedResponse['points']
        wins = parsedResponse['wins']
        driver = parsedResponse['Driver']['givenName'] + ' ' + parsedResponse['Driver']['familyName']
        constructor = parsedResponse['Constructors'][0]['name']

        reply = """{}, driving for {}, won the {} Formula1 championship 
                with a total of {} points and {} winned races.""".format(driver, constructor, year, points, wins)

        dispatcher.utter_message(reply)

        return [SlotSet('year', year)]

class ActionSearchDriver(Action):
    def name(self) -> Text:
        return 'action_search_driver'
    
    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        driver = tracker.get_slot('driver')

        print(driver)

        url = 'http://ergast.com/api/f1/drivers.json?limit=1000'
        response = requests.get(url)
        jsonResponse = response.json()

        parsedResponse = jsonResponse['MRData']['DriverTable']['Drivers']

        best_match, confidence = searchDriver(driver, parsedResponse)

        url = f'http://ergast.com/api/f1/drivers/{best_match}.json'
        response = requests.get(url)
        jsonResponse = response.json()

        driver = jsonResponse['MRData']['DriverTable']['Drivers'][0]

        wikipedia = driver['url']

        wiki_id = wikipedia.rsplit('/', 1)[1]

        full_name, description = searchDriverDescription(wiki_id)

        if len(description) < 200:
            full_name, description = searchDriverDescription(wiki_id, type=2)

        more_info = """\nYou can find more information about {} at {}.""".format(full_name, wikipedia)

        reply = description + more_info

        dispatcher.utter_message(reply)

        return [SlotSet('driver', best_match)]