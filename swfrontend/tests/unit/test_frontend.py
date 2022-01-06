import pytest
import app 
from app import app as client_app
from pprint import pprint

test_client = client_app.test_client()

@pytest.fixture(autouse=True)
def backend_patch(mocker):
    mocker.patch(
        'app.proxy.update_database',
        return_value = True
    )
    mocker.patch(
        'app.proxy.get_items_count',
        return_value = {'people': 99, 'planets': 42}
    )
    def get_message(path: str):
        if path == 'people':
            return [
                {
                    "name": "Ackbar",
                    "uid": 27,
                    "homeworld": "Mon Cala",
                    "objtype": "person",
                    "gender": "male"
                }
            ]  
        elif path == 'planets':
            return [
                {
                    "name": "Alderaan",
                    "uid": 2,
                    "objtype": "planet",
                    "climate": "temperate",
                    "gravity": "1 standard"
                }
            ]
        elif path.startswith("residents/"):
            planet_name = path.split("/")[1]
            return {
                'name': planet_name, 
                'residents': [{"gender": "male", "name": "Anakin Skywalker"}]
            }
    mocker.patch(
        'app.proxy.get_message',
        side_effect=get_message
    )



def test_database_update(mocker):   
    response = test_client.post("/")
    assert response.status_code == 200
    assert b"People: 99" in response.data
    assert b"Planets: 42" in response.data    

def test_frontend_get_people(mocker):
    response = test_client.get("/people")
    assert response.status_code == 200
    assert b"Ackbar" in response.data
    assert b"Mon Cala" in response.data
    assert b"male" in response.data
    
def test_frontend_get_planets(mocker):
    response = test_client.get("/planets")
    # pprint(response.data)
    assert response.status_code == 200
    assert b"Alderaan" in response.data
    assert b"temperate" in response.data
    assert b"1 standard" in response.data

def test_frontend_get_residents(mocker):
    response = test_client.get("/residents/TestPlanet")
    assert response.status_code == 200
    assert b"TestPlanet" in response.data

def test_frontend_get_allresidents(mocker):
    response = test_client.get("/allresidents")
    pprint(response.data)
    assert response.status_code == 200
    assert b"<td>1</td>" in response.data
