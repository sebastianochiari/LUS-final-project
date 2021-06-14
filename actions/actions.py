# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

import requests
import datetime

from utils import searchConstructor, searchDriver, searchDriverDescription

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.types import DomainDict
from rasa_sdk.events import Form, SlotSet

class ActionSearchDriverByConstructor(Action):
    def name(self) -> Text:
        return "action_search_drivers_by_constructor"
    
    async def run(self, dispatcher: "CollectingDispatcher", tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:

        constructor = tracker.get_slot('constructor')

        print(constructor)

        year_slot = tracker.get_slot('year')

        if year_slot is None:
            year = 'current'
            when = 'are'
        else:
            year = int(year_slot)
            when = 'were'

        url = f'http://ergast.com/api/f1/{year}/constructors.json'
        response = requests.get(url)
        jsonResponse = response.json()

        parsedResponse = jsonResponse['MRData']['ConstructorTable']['Constructors']

        best_match, confidence = searchConstructor(constructor, parsedResponse)

        print(best_match)
        print(confidence)

        if confidence >= 0.8:
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
        if tracker.get_slot("circuit") != "None":
            return ["is_interested_in_driver"] + slots_mapped_in_domain
        if tracker.get_slot("is_interested_in_driver") is True:
            return ["driver"] + slots_mapped_in_domain
        return slots_mapped_in_domain

    async def extract_is_interested_in_driver(
        self,
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict"
    ) -> Dict[Text, Any]:
        intent = tracker.get_intent_of_latest_message()
        return {"is_interested_in_driver": intent == "affirm"}

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
            return {"driver": slot_value}

class ActionSearchRaceResult(Action):
    def name(self) -> Text:
        return 'action_search_race_result'

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message('Form triggered')

        return []

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

        best_match = searchDriver(driver, parsedResponse)

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