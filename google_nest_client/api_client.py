import requests
import time
from collections import namedtuple

from google_nest_client.device import get_device_label


API_URI = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/'
REFRESH_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'


OAuthCredentials = namedtuple('OAuthCredentials', (
    'client_id',
    'client_secret',
    'refresh_token',
    'access_token',
    'token_expiry',
    'scope',
    'token_type',
))


class AuthenticationError(Exception):
    pass


class GoogleNestAPIClient():
    def __init__(self, project_id, client_id, client_secret, refresh_token):
        self.project_id = project_id

        self.save_credentials(
            OAuthCredentials(
                client_id=client_id,
                client_secret=client_secret,
                refresh_token=refresh_token,
                access_token=None,
                token_expiry=0,
                scope=None,
                token_type=None,
            )
        )

    def get_credentials(self):
        return self.creds

    def save_credentials(self, creds):
        self.creds = creds

    def get_access_token(self):
        creds = self.get_credentials()
        if not creds.access_token or creds.token_expiry < time.time():
            new_creds = self.refresh_access_token(creds)
            self.save_credentials(new_creds)
            return new_creds.access_token
        else:
            return creds.access_token

    def refresh_access_token(self, creds):
        new_creds = requests.post(
            REFRESH_TOKEN_URI,
            headers={
                'Content-type': 'application/json',
            },
            params={
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'refresh_token': creds.refresh_token,
                'grant_type': 'refresh_token',
            },
        ).json()

        if not new_creds['access_token']:
            raise AuthenticationError

        return OAuthCredentials(
            client_id=self.creds.client_id,
            client_secret=self.creds.client_secret,
            refresh_token=self.creds.refresh_token,
            access_token=new_creds['access_token'],
            token_expiry=int(time.time()) + new_creds['expires_in'],
            scope=new_creds['scope'],
            token_type=new_creds['token_type'],
        )

    def api_get(self, endpoint):
        resp = requests.get(
            API_URI + self.project_id + endpoint,
            headers={
                'Authorization': 'Bearer ' + self.get_access_token(),
                'Content-type': 'application/json',
            },
        )

        try:
            resp.raise_for_status()
        except requests.HTTPError as ex:
            if ex.response.status_code in (401, 403):
                raise AuthenticationError

        return resp.json()

    def api_post(self, endpoint, json=None):
        resp = requests.post(
            API_URI + self.project_id + endpoint,
            headers={
                'Authorization': 'Bearer ' + self.get_access_token(),
                'Content-type': 'application/json',
            },
            json=json,
        )

        try:
            resp.raise_for_status()
        except requests.HTTPError as ex:
            if ex.response.status_code in (401, 403):
                raise AuthenticationError

        return resp.json()

    def get_structures(self):
        return self.api_get(
            '/structures'
        )['structures']

    def get_devices(self):
        return self.api_get(
            '/devices'
        )['devices']

    def get_device(self, device_id):
        return self.api_get('/devices/' + device_id)

    def get_devices_by_type(self, device_type):
        return [
            device for device in self.get_devices()
            if device['type'] == device_type
        ]

    def get_devices_by_type_and_label(self, device_type, label):
        return [
            device for device in self.get_devices_by_type(device_type)
            if get_device_label(device) == label
        ]

    def execute_command(self, device_id, command, params):
        return self.api_post(
            '/devices/' + device_id + ':executeCommand',
            json={
                'command': command,
                'params': params,
            },
        )
