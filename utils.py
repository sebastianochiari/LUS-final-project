
import requests

from difflib import SequenceMatcher

def searchDriver(driverToBeFound, driversList):
    
    best_match = ''
    confidence = 0

    for i in range(0, len(driversList)):
        id = driversList[i]['driverId']
        full_name = driversList[i]['givenName'] + ' ' + driversList[i]['familyName']
        temp_confidence = SequenceMatcher(a=full_name,b=driverToBeFound).ratio()
        if temp_confidence < 0.7:
            surname = driversList[i]['familyName']
            temp_confidence = SequenceMatcher(a=surname, b=driverToBeFound).ratio()
        if temp_confidence > confidence:
            confidence = temp_confidence
            best_match = id

    return best_match, confidence

def searchConstructor(constructorToBeFound, constructorList):
    
    best_match = ''
    confidence = 0

    for i in range(0, len(constructorList)):
        id = constructorList[i]['constructorId']
        name = constructorList[i]['name']
        temp_confidence = SequenceMatcher(a=name,b=constructorToBeFound).ratio()
        if temp_confidence > confidence:
            confidence = temp_confidence
            best_match = id

    return best_match, confidence

def searchGrandPrix(circuitToBeFound, raceSchedule):

    best_match = 0
    confidence = 0

    race_names = []

    for entry in raceSchedule:
        tmp = []
        tmp.append(entry['raceName'])
        tmp.append(entry['Circuit']['circuitName'])
        tmp.append(entry['Circuit']['Location']['locality'])
        tmp.append(entry['Circuit']['Location']['country'])
        race_names.append(tmp)

    for i in range(0, len(race_names)):
        for entry in race_names[i]:
            temp_confidence = SequenceMatcher(a=entry,b=circuitToBeFound).ratio()
            if temp_confidence > confidence:
                confidence = temp_confidence
                best_match = i + 1

    return best_match, confidence, race_names[best_match-1]


def searchDriverDescription(id, type = 1):

    if type == 1:
        simple_url = f"https://simple.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={id}"
    elif type == 2:
        simple_url = f"https://en.wikipedia.org/w/api.php?format=json&action=query&prop=extracts&exintro&explaintext&redirects=1&titles={id}"

    print(simple_url)

    response = requests.get(simple_url)
    jsonResponse = response.json()

    description = jsonResponse['query']['pages']

    pageid = 0
    for key in description:
        pageid = key
        continue

    full_name = description[pageid]['title']

    if 'extract' in description[pageid]:
        description = (description[pageid]['extract']).split('\n')[0]
    else:
        description = ""

    return full_name, description