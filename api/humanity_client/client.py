import json
import os
from datetime import datetime

import aiohttp
from aiohttp import FormData

from humanity_client.Employees import Employees
from humanity_client.LeaveTypes import LeaveTypes
from humanity_client.Leaves import Leaves
from humanity_client.Locations import Locations
from humanity_client.Positions import Positions
from humanity_client.Shifts import Shifts
from humanity_client.Trades import Trades

# Updated to ensure we have the complete URL including the path
base_api = os.environ.get('BASE_API_URL', 'http://localhost:8081')
if not base_api.endswith('/api/'):
    base_api = f"{base_api}/api/"

dir_path = os.path.dirname(os.path.realpath(__file__))

class Client:
    def __init__(self, authentication_creds = None, log_interactions = False ):
        self.authentication_creds = authentication_creds
        self.Shifts = Shifts( self )
        self.Trades = Trades( self )
        self.Employees = Employees( self )
        self.LeaveTypes = LeaveTypes( self )
        self.Leaves = Leaves( self )
        self.Locations = Locations( self )
        self.Positions = Positions( self )
        self.log_interactions = log_interactions
        ...

    def __del__(self):
        ...

    async def get( self, route, params = None ):
        if params is None:
            params = { }
        final_params = {
            'access_token': self.authentication_creds["access_token"],
            **params
        }
        async with aiohttp.ClientSession() as session:
            async with session.get( f'{base_api}v2{route}',  params = final_params ) as response:
                status = response.status
                response_json = None
                if status == 200:
                    response_json = await response.json()
                await self.log_interaction( 'get', route, None, params, status, response_json )
                return status, response_json

    async def post( self, route, json_data = None, params = None ):
        if json_data is None:
            json_data = { }
        if params is None:
            params = { }
        final_params = {
            'access_token': self.authentication_creds["access_token"],
            **params
        }
        async with aiohttp.ClientSession() as session:
            async with session.post( f'{base_api}v2{route}',  params = final_params, json = json_data ) as response:
                status = response.status
                response_json = None
                if status == 200:
                    response_json = await response.json()
                await self.log_interaction( 'post', route, json_data, params, status, response_json )
                return status, response_json

    async def log_interaction( self, method, route, json_data=None, params=None, status=None, response_json = None ):
        if not self.log_interactions:
            return
        try:
            os.mkdir( f'{dir_path}/../logs/client/{method}/{route}' )
        except:
            ...
        try:
            with open( f'{dir_path}/../logs/client/{method}/{route}/{datetime.now().isoformat()}.json', 'w' ) as json_file:
                json.dump(
                    {
                        'json_data': json_data,
                        'params': params,
                        'status': status,
                        'response': response_json
                    },
                    json_file,
                    indent = 4
                )
        except:
            ...


    async def login( self, username, password ):
        return await self.login_data_api( username, password )

    async def login_data_api( self, username, password ):
        form_data = FormData(
            fields = {
                "data": json.dumps({
                    "key": os.environ['LOGIN_KEY'],
                    "module": "staff.login",
                    "method": "GET",
                    "username": username,
                    "password": password
                } )
            }
        )
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        async with aiohttp.ClientSession() as session:
            async with session.post( f'{base_api}', data = form_data, headers=headers ) as response:
                if response.status == 200:
                    response_json = await response.text()
                    response_json = json.loads( response_json )

                    if response_json['status'] != 1:
                        return False
                    if 'token' not in response_json or response_json['token'] is None:
                        return False
                    response_json['access_token'] = response_json['token']
                    self.authentication_creds = response_json
                else:
                    return False
                return True

