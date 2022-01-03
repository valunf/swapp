
from json import encoder
import boto3
from boto3.dynamodb.conditions import Attr, Key
import os
from pprint import pprint
from dataclasses import dataclass, field
import json
import requests
from utils import DecimalEncoder


STARWARS_API = "swapi.py4e.com" # Default
# STARWARS_API = "www.swapi.tech"
TYPES_MAP = {'planets': 'planet', 'people': 'person'}

local_dynamodb_url = 'http://172.16.22.2:8000'
region = os.environ['AWS_REGION'] or 'eu-central-1'
if os.environ['AWS_SAM_LOCAL']:
    DBD = boto3.resource('dynamodb', region_name=region, endpoint_url=local_dynamodb_url)
else:
    DBD = boto3.resource('dynamodb', region_name=region)
TABLE_NAME = os.environ['TABLE_NAME']

def create_table():
    tbl = DBD.create_table(
        TableName=TABLE_NAME,
        KeySchema=[
            {
                'AttributeName': 'objtype',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'name',
                'KeyType': 'RANGE'
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'objtype',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'name',
                'AttributeType': 'S'
            },
            {
                'AttributeName': 'uid',
                'AttributeType': 'N'
            }
        ],
        GlobalSecondaryIndexes = [
            {
                "IndexName": "uid",
                "KeySchema": [
                    {
                        'AttributeName': 'uid',
                        'KeyType': 'HASH'
                    }
                ],
                "Projection": {
                    "ProjectionType": "ALL"
                },
                'ProvisionedThroughput' :{
                    'ReadCapacityUnits': 1,
                    'WriteCapacityUnits': 1,
                }
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 5,
            'WriteCapacityUnits': 5
        }
    )
    return tbl


def delete_table():
    try:
        table = DBD.Table(TABLE_NAME)
        table.delete()
    except:
        pass


def update_table(sw_api: str = STARWARS_API) -> dict:
    delete_table()
    table = create_table()
    try:
        for t in ['planets', 'people']: # planets must be first
            next_page = f'https://{sw_api}/api/{t}?page=1'
            while True:
                response = requests.get(next_page)
                if response is None:
                    break
                r: dict = response.json()
                for obj in r['results']:
                    add_object_to_db(table=table, obj_type=t, json_obj=obj)
                next_page = r['next']
                if not next_page:
                    break
    except Exception as e:
        print("Error while updating database!")
        print(e)
        return False
    return True

def add_object_to_db(table, obj_type: str, json_obj: dict) -> bool:
    result = False
    t = TYPES_MAP[obj_type]
    d = {'objtype': t}
    store_fields_dict = {
        'planet':[ 'name', 'gravity', 'climate'  ],
        'person':[ 'name', 'gender', 'homeworld' ]
        }
    # pprint(json_obj)
    d['uid'] = int(json_obj['url'].strip("/").split("/")[-1])
    # print(f"type({t}) -- uid({d['uid']})")
    for f in store_fields_dict[t]:
        field_data = json_obj[f]
        if f == 'homeworld':
            homeworld_id = int(field_data.strip("/").split("/")[-1])
            q =  table.query(
                IndexName='uid',
                KeyConditionExpression=Key('uid').eq(homeworld_id),
                FilterExpression=Key('objtype').eq('planet')
                )['Items']
            # pprint(q)
            if len(q) > 0:
                field_data = q[0]['name']
        d[f] = field_data
    try:
        response = table.put_item(Item=d)
        result = True
    except Exception as e:
        pprint(e)
    return result


def get_residents(table, planet_name) -> list:
    residents = []
    scan_kwargs = {
        'FilterExpression': Key('homeworld').eq(planet_name),
        'ProjectionExpression': "#n, gender",
        'ExpressionAttributeNames': {"#n": "name"}
    }
    done = False
    start_key = None
    while not done:
        if start_key:
            scan_kwargs['ExclusiveStartKey'] = start_key
        response = table.scan(**scan_kwargs)
        residents.extend(response.get('Items', []))
        start_key = response.get('LastEvaluatedKey', None)
        done = start_key is None
    return residents

def lambda_handler(event, context):
    msg = {"error": "empty"}
    status = 200
    args = event.get('path').split("/")
    http_method = event.get('httpMethod')
    tbl_names = [t.name for t in DBD.tables.all()]
    # pprint(event)
    if TABLE_NAME not in tbl_names:
        table = create_table()
    else:
        table = DBD.Table(TABLE_NAME)
    
    if http_method == 'GET':
        type_key = TYPES_MAP.get(args[1].lower())
        if type_key:
            name = args[2] if 2 < len(args) else None
            if name:
                response = table.get_item(Key={'objtype': type_key, 'name': str(name)})
                pprint(response)
                msg = response.get('Items')
            else:
                msg = table.query(KeyConditionExpression=Key('objtype').eq(type_key)).get('Items')
        if args[1].lower() == 'residents':
            planet_name = str(args[2]) if 2 < len(args) else None
            if planet_name:
                response = table.get_item(Key={'objtype': 'planet', 'name': planet_name})
                if response.get('Item'):
                    residents = get_residents(table, planet_name)
                    if len(residents) > 0:
                        msg = {'name': planet_name, 'residents': residents}
                    else:
                        msg = {'error': f"No residents found for planet {planet_name}"}
                else:
                    msg = {'error': f"Planet {planet_name} not found"}
            else:
                msg = {'error': "Planet name is empty"}
            
    elif http_method == 'PUT' and args[1].lower() == 'update':
        print("===UPDATE DATABASE===")
        if event['queryStringParameters']:
            updated_successfuly = update_table(event['queryStringParameters']['sw_api'])
        else:
            updated_successfuly = update_table()
        status = 201 if updated_successfuly else 520

    return {
        "statusCode": status,
        "body": json.dumps({
            "message": msg
        }, cls=DecimalEncoder)
    }
