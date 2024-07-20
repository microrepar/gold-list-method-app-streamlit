import datetime
from typing import List

import requests

from config import Config
from src.core.notebook import Notebook
from src.core.pagesection import Group, PageSection, PageSectionRepository
from src.core.shared.utils import date_to_string, string_to_date

from .. import repository_map


@repository_map
class ApiPageSectionRepository(PageSectionRepository):
    """API implementation of PageSectionRepository"""

    def __init__(self):
        self.url = Config.API_URL + 'pagesections/'
        self.token = Config.API_TOKEN
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.querystring = {}

    def registry(self, entity: PageSection) -> PageSection:
        url = self.url
        pagesection_dict = entity.to_dict()
        pagesection_dict.pop('id')
        pagesection_dict.pop('updated_at')
        

        self.querystring.update(pagesection_dict)
        response = requests.post(url, headers=self.headers, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()
        
        entity.id = response_json.get('id')
        entity.created_at = string_to_date(response_json.get('created_at'))
        entity.updated_at = string_to_date(response_json.get('updated_at'))
        entity.page_number = response_json.get('page_number')
        
        pagesection = PageSection(
            id_=response_json.get('id'),
            created_at=string_to_date(response_json.get('created_at')),
            updated_at=string_to_date(response_json.get('updated_at')),
            notebook=entity.notebook,
            page_number=response_json.get('page_number'),
            group=Group(response_json.get('group')),
            distillation_at=string_to_date(response_json.get('distillation_at')),
            distillated=response_json.get('distillated'),
            distillation_actual=string_to_date(response_json.get('distillation_actual')),
            created_by=response_json.get('created_by'),
            sentencelabels=entity.sentencelabels
        )
        return pagesection
    
    def update(self, entity: PageSection) -> PageSection:
        url = self.url + f'{entity.id}'
        pagesection_dict = entity.to_dict()
        pagesection_dict.pop('id')
        pagesection_dict.pop('created_at')
        pagesection_dict.pop('updated_at')
        pagesection_dict.pop('created_by_id')
        pagesection_dict.pop('notebook_id')        
        pagesection_dict = {k: v for k, v in pagesection_dict.items() if v}

        self.querystring.update(pagesection_dict)
        response = requests.put(url, headers=self.headers, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()
        
        pagesection = PageSection(
            id_=response_json.get('id'),
            updated_at=response_json.get('updated_at'),
            created_at=response_json.get('created_at'),
            notebook=entity.notebook,
            page_number=response_json.get('page_number'),
            group=Group(response_json.get('group')),
            distillation_at=response_json.get('distillation_at'),
            distillated=response_json.get('distillated'),
            distillation_actual=response_json.get('distillation_actual'),
            created_by=entity.created_by,
            sentencelabels=entity.sentencelabels
        )
        return pagesection

    def get_all(self) -> List[PageSection]:
        return []
    
    def get_by_id(self, entity: PageSection) -> PageSection:
        pass

    def find_by_field(self, entity: PageSection) -> List[PageSection]:
        url = self.url + f'find_by_field/'
        filters = {k: v for k, v in entity.__dict__.items() if not k.startswith('_') and v is not None}
        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False:
                continue
            if isinstance(value, Notebook):
                attr = "notebook_id"
                value = value.id
            elif isinstance(value, Group):
                attr = "group"
                value = value.value
            elif isinstance(value, PageSection):
                attr = "created_by_id"
                value = value.created_by.id
            elif attr in "created_at":
                if isinstance(value, datetime.date):
                    value = date_to_string(value)
                    # value = pd.to_datetime(value).strftime("%Y-%m-%d")
                elif "#" in value:
                    value = None
            elif attr in 'distillation_at':
                if value:
                    value = date_to_string(value)
            elif attr in "section_number distillated distillation_at":
                ...
            else:
                raise Exception(
                    f'This field "{attr}" cannot be used to find PageSection objects!'
                )
            kwargs[attr] = value
        
        self.querystring.update(kwargs)
        response = requests.post(url, headers=self.headers, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()

        pagesection_list = []
        for pagesection_dict in response_json:

            pagesection = PageSection(
                id_=pagesection_dict.get('id'),
                created_at=string_to_date(pagesection_dict.get('created_at')),
                created_by=entity.created_by,
                notebook=entity.notebook,
                sentencelabels=entity.sentencelabels,
                page_number=pagesection_dict.get('page_number'),
                group=Group[pagesection_dict.get('group')],
                distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
                distillated=pagesection_dict.get('distillated'),
                distillation_actual=pagesection_dict.get('distillation_actual')
            )

            if 'notebook_id' not in kwargs.keys():
                pagesection.notebook = Notebook(id_=pagesection_dict.get('notebook'))
            else:
                pagesection.notebook = entity.notebook
            pagesection_list.append(pagesection)
            
        return pagesection_list

    def get_last_page_number(self, entity: PageSection = None) -> int:
        url = self.url + f'get_last_pagenumber/'
        response = requests.get(url, headers=self.headers, params={'notebook_id': entity.notebook.id})
        response.raise_for_status()
        response_json = response.json()
        return response_json.get('last_pagenumber')

    def get_sentences_by_group(self, entity: PageSection):
        url = self.url + f'get_sentencelabel_by/{entity.notebook.id}/{entity.group.value}'
        response = requests.get(url)
        response.raise_for_status()
        response_json = response.json()
                
        from src.core.sentencetranslation import SentenceTranslation
        sentence_list = []
        for sentencetranslation_dict in response_json:
            sentencetranslation = SentenceTranslation(
                id_=sentencetranslation_dict.get('id'),
                created_at=string_to_date(sentencetranslation_dict.get('created_at')),                
                updated_at=string_to_date(sentencetranslation_dict.get('updated_at')),                
                foreign_language=sentencetranslation_dict.get('foreign_language_sentence'),
                mother_tongue=sentencetranslation_dict.get('mother_language_sentence'),
                foreign_idiom=sentencetranslation_dict.get('foreign_language_idiom'),
                mother_idiom=sentencetranslation_dict.get('mother_language_idiom')
            )
            sentence_list.append(sentencetranslation)        
        return sentence_list 

    def validate_sentences(self, entity: PageSection) -> List[str]:
        return []
    
    def remove(self, entity: PageSection) -> bool:
        url = self.url + f'{entity.id}'
        response = requests.delete(url)
        response.raise_for_status()
        success = response.json().get('success')
        return success

    def update_sentencelabel(self, entity: PageSection):
        pass
        