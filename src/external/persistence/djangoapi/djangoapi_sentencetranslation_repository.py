import datetime
from typing import List

import requests

from config import Config
from src.core.shared.utils import string_to_date
from src.core.sentencetranslation import SentenceTranslation, SentenceTranslationRepository
 

from .. import repository_map


@repository_map
class ApiSentenceTranslationRepository(SentenceTranslationRepository):
    """API implementation of PageSectionRepository"""

    def __init__(self):
        self.url = Config.API_URL + 'sentencetranslations/'
        self.token = Config.API_TOKEN
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.querystring = {}

    def registry(self, entity: SentenceTranslation) -> SentenceTranslation:
        url = self.url
        sentencetranslation_dict = entity.to_dict()
        sentencetranslation_dict.pop('id')
        sentencetranslation_dict.pop('created_at')
        sentencetranslation_dict.pop('updated_at')
        response = requests.post(url, headers=self.headers, json=sentencetranslation_dict)
        if response.status_code != 200:
            res_json = response.json()
            raise Exception( res_json.get('message', res_json.get('detail')))
        sentencetranslation_dict = response.json()

        sentencetranslation = SentenceTranslation(
            id_=sentencetranslation_dict.get('id'),
            created_at=string_to_date(sentencetranslation_dict.get('created_at')),
            updated_at=string_to_date(sentencetranslation_dict.get('updated_at')),
            foreign_language=sentencetranslation_dict.get('foreign_language_sentence'),
            mother_tongue=sentencetranslation_dict.get('mother_language_sentence'),
            foreign_idiom=sentencetranslation_dict.get('foreign_language_idiom'),
            mother_idiom=sentencetranslation_dict.get('mother_language_idiom')
        )
        return sentencetranslation
    
    def get_all(self) -> List[SentenceTranslation]:
        return []
    
    def get_by_id(self, entity: SentenceTranslation) -> SentenceTranslation:
        pass

    def find_by_field(self, entity: SentenceTranslation) -> List[SentenceTranslation]:
        url = self.url + f'find_by_field/'
        filters = {k: v for k, v in entity.__dict__.items() if not k.startswith('_') and v is not None}
        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False:
                continue
            if attr in 'id':
                ...
            elif attr in 'foreign_language':
                attr = 'foreign_language_sentence'                
            elif attr in 'foreign_idiom':
                attr = 'foreign_language_idiom'                
            elif attr in 'mother_idiom':
                attr = 'mother_language_idiom'                
            else:
                raise Exception(
                    f'This field "{attr}" cannot be used to find SentenceTranslation objects!'
                )
            kwargs[attr] = value
        
        response = requests.post(url, headers=self.headers, json=kwargs)
        response.raise_for_status()
        response_json = response.json()
        
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

    def update(self, entity: SentenceTranslation) -> SentenceTranslation:
        pass

    def remove(self, entity: SentenceTranslation):
        pass

