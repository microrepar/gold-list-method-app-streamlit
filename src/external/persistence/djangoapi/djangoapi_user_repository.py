from typing import List

import requests

from config import Config
from src.core.shared.utils import string_to_date
from src.core.user import User, UserRepository
from src.external.persistence import repository_map


@repository_map
class ApiUserRepository(UserRepository):
    
    def __init__(self):
        self.url = Config.API_URL + 'users/'
        self.token = Config.API_TOKEN
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.querystring = {}
    
    def registry(self, entity: User) -> User:
        raise Exception('"registry" method in "ApiUserRepository" is not implemented')

    def get_all(self, entity: User) -> List[User]:
        url = self.url
        response = requests.request('GET', url)
        response.raise_for_status()
        response_json = response.json()
        user_list = []
        for user_dict in response_json:
            user = User(
                id_=user_dict.get('id'),
                password=user_dict.get('password2'),
                created_at=string_to_date(user_dict.get('created_at')),
                status=user_dict.get('status'),
                name=user_dict.get('name'),
                age=user_dict.get('age'),
                email=user_dict.get('email'),
                profile=user_dict.get('profile'),
                username=user_dict.get('username'),
                repeat_password=user_dict.get('repeat_password')
            )
            user_list.append(user)
        return user_list

    def update(self, entity: User) -> User:
        url = self.url + f'{entity.id}'        
        self.querystring['name']            = entity.name
        self.querystring['email']           = entity.email
        response = requests.put(url, headers=self.headers, json=self.querystring)
        response.raise_for_status()
        user_dict = response.json()
        user = User(
            id_=user_dict.get('id'),
            password=user_dict.get('password2'),
            created_at=user_dict.get('created_at'),
            status=user_dict.get('status'),
            name=user_dict.get('name'),
            age=user_dict.get('age'),
            email=user_dict.get('email'),
            profile=user_dict.get('profile'),
            username=user_dict.get('username'),
            repeat_password=user_dict.get('repeat_password')
        )
        return user

    def find_by_field(self, entity: User) -> List[User]:
        url = self.url + f'find_by_field/'
        filters = {k: v for k, v in entity.__dict__.items() if not k.startswith('_') and v is not None}
        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: 
                continue                        
            elif attr in 'username email id':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find Users!')            
            kwargs[attr] = value

        self.querystring.update(kwargs)
        response = requests.post(url, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()
        user_list = []
        for user_dict in response_json:
            user = User(
                id_=user_dict.get('id'),
                password=user_dict.get('password2'),
                created_at=string_to_date(user_dict.get('created_at')),
                status=user_dict.get('status'),
                name=user_dict.get('name'),
                age=user_dict.get('age'),
                email=user_dict.get('email'),
                profile=user_dict.get('profile'),
                username=user_dict.get('username'),
                repeat_password=user_dict.get('repeat_password')
            )
            user_list.append(user)
        return user_list
    
    def remove(self, entity: User) -> bool:        
        raise Exception('"remove" method in "ApiUserRepository" is not implemented')
        
    def get_by_id(self, entity: User) -> User:
        raise Exception('"get_by_id" method in "ApiUserRepository" is not implemented')