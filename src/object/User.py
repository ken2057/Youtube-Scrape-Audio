import requests
import json
from getpass import getpass
# ------------------------------------------------------------------------------
from src.config import API
# ------------------------------------------------------------------------------

class User():
    def __init__(self):
        self.username = None
        self.password = None

    def import_(self):
        '''Import playlist from api'''
        if self.username == None:
            self.login_()
        params={'username': self.username, 'password': self.password}
        r = requests.get(API + 'import', params=params)
        return json.loads(r.content)

    def export_(self, playlists):
        '''Export playlist into api'''
        if self.username == None:
            self.login_()

        params={
            'username': self.username, 
            'password': self.password, 
        }
        
        r = requests.post(
            API + 'export', 
            params=params,
            json={'playlists': playlists}
        )
        return json.loads(r.content)

    def login_(self):
        '''Change username, password'''
        self.username = input('Username: ')
        self.password = getpass('Password: ')

    def reset_all(self):
        self.username = None
        self.password = None