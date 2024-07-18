import datetime
from typing import List

import requests

from config import Config
from src.core.notebook import Notebook, NotebookRepository
from src.core.shared.utils import string_to_date
from src.core.user.model.user import User

from .. import repository_map


@repository_map
class ApiNotebookRepository(NotebookRepository):
    """API implementation of NotebookRepository"""

    def __init__(self):
        self.url = Config.API_URL + 'notebooks/'
        self.token = Config.API_TOKEN
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.querystring = {}

    def get_all(self) -> List[Notebook]:
        url = self.url
        response = requests.request('GET', url)
        response.raise_for_status()
        response_json = response.json()
        notebook_list = []
        for notebook_dict in response_json:
            user_dict = notebook_dict.get('user')
            user = None
            if user_dict:
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
            notebook = Notebook(
                name=notebook_dict.get('name'),
                id_=notebook_dict.get('id'),
                created_at=string_to_date(notebook_dict.get('created_at')),
                updated_at=string_to_date(notebook_dict.get('updated_at')),
                sentence_list_size=notebook_dict.get('sentence_list_size'),
                days_period=notebook_dict.get('days_period'),
                foreign_idiom=notebook_dict.get('foreign_idiom'),
                mother_idiom=notebook_dict.get('mother_idiom'), 
                user=user               
            )
            notebook_list.append(notebook)
        return notebook_list
    
    def get_by_id(self, entity: Notebook) -> Notebook:
        notebook_filter = Notebook(id_=entity.id)
        notebooks = self.find_by_field(notebook_filter)
        if notebooks:
            return notebooks[-1]
        raise Exception(f'No notebooks were found with id={entity.id}.')
  
    def find_by_field(self, entity: Notebook) -> List[Notebook]:
        url = self.url + f'find_by_field/'
        filters = {k: v for k, v in entity.__dict__.items() if not k.startswith('_') and v is not None}
        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False: continue

            if attr in 'created_at':
                if isinstance(value, datetime.date):
                    value = value
                    # value = pd.to_datetime(value).strftime("%Y-%m-%d")
            elif attr in 'user':
                attr = 'user_id'
                value = value.id
            elif attr in 'id name sentence_list_size days_period foreign_idiom mother_idiom':
                ...
            else:
                raise Exception(f'This field "{attr}" cannot be used to find Notebook objects!')
            kwargs[attr] = value
        self.querystring.update(kwargs)
        response = requests.post(url, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()
        notebook_list = []
        for notebook_dict in response_json:
            user_dict = notebook_dict.get('user')
            user = None
            if user_dict:
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
            
            notebook = Notebook(
                name=notebook_dict.get('name'),
                id_=notebook_dict.get('id'),
                created_at=notebook_dict.get('created_at'),
                updated_at=notebook_dict.get('updated_at'),
                sentence_list_size=notebook_dict.get('sentence_list_size'),
                days_period=notebook_dict.get('days_period'),
                foreign_idiom=notebook_dict.get('foreign_idiom'),
                mother_idiom=notebook_dict.get('mother_idiom'), 
                user=user               
            )
            
            notebook_list.append(notebook)
        return notebook_list

    def registry(self, entity: Notebook) -> Notebook:
        url = self.url
        notebook_dict = entity.to_dict()
        notebook_dict.pop('id')
        notebook_dict.pop('created_at')
        notebook_dict.pop('updated_at')
        response = requests.post(url, headers=self.headers, json=notebook_dict)
        if response.status_code != 200:
            raise Exception(response.json().get('message'))
        notebook_dict = response.json()

        user_dict = notebook_dict.get('user')
        user = None
        if user_dict:
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
            
        
        notebook = Notebook(
            name=notebook_dict.get('name'),
            id_=notebook_dict.get('id'),
            created_at=notebook_dict.get('created_at'),
            updated_at=notebook_dict.get('updated_at'),
            sentence_list_size=notebook_dict.get('sentence_list_size'),
            days_period=notebook_dict.get('days_period'),
            pagesection_list=notebook_dict.get('pagesection_list'),
            foreign_idiom=notebook_dict.get('foreign_idiom'),
            mother_idiom=notebook_dict.get('mother_idiom'), 
            user=user               
        )
        return notebook

