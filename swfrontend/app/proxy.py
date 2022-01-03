from pprint import pprint
from app import app
import requests
from urllib import parse
from cachetools import cached, TTLCache

BACKEND_URI = app.config['BACKEND_URI']
TTL_TIME = 120

# TODO Get data from backend
@cached(cache=TTLCache(maxsize=1024, ttl=TTL_TIME))
def get_message(path: str) -> list:
    resp = requests.get(f"{BACKEND_URI}/{path}")
    if resp.status_code == 200:
        msg = resp.json()
        return msg['message']
    else:
        return []

def get_planets() -> list:
    return get_message('planets')

def get_people() -> list:
    return get_message('people')

def get_allresidents() -> list:
    people = get_people()
    planets = dict()
    for person in people:
        hw = person['homeworld']
        if hw in planets.keys():
            planets[hw].append(person['name'])
        else:
            planets[hw] = [person['name'],]
    return [{'name': k, 'count': len(v)} for k, v in planets.items()]

def get_planet(name: str) -> dict:
    msg = get_message(parse.quote(f'residents/{name}'))
    return msg

def get_items_count():
    return {'people': len(get_people()), 'planets': len(get_planets())}

def update_database() -> bool:
    print('Update database from source')
    resp = requests.put(f"{BACKEND_URI}/update")
    if resp.status_code == 201:
        return True
    return False