from typing import List

import requests

from config import Config
from src.core.pagesection import PageSection
from src.core.sentencelabel import SentenceLabel, SentenceLabelRepository
from src.core.sentencetranslation import SentenceTranslation
from src.core.shared.utils import string_to_date

from .. import repository_map


@repository_map
class ApiSentenceLabelRepository(SentenceLabelRepository):
    """API implementation of PageSectionRepository"""

    def __init__(self):
        self.url = Config.API_URL + 'sentencelabels/'
        self.token = Config.API_TOKEN
        self.headers = headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        self.querystring = {}

    def get_all(self) -> List[SentenceLabel]:
        return []
    
    def registry(self, entity: SentenceLabel) -> SentenceLabel:
        pass
    
    def get_by_id(self, entity: SentenceLabel) -> SentenceLabel:
        pass

    def find_by_field(self, entity: SentenceLabel) -> List[SentenceLabel]:
        url = self.url + f'find_by_field/'
        filters = {k: v for k, v in entity.__dict__.items() if not k.startswith('_') and v is not None}
        kwargs = {}
        for attr, value in filters.items():
            if bool(value) is False:
                continue
            if isinstance(value, PageSection):
                attr = 'pagesection_id'
                value = value.id
            elif attr in 'id':
                pass
            else:
                raise Exception(
                    f'This field "{attr}" cannot be used to find SentenceLabel objects!'
                )
            kwargs[attr] = value
        
        self.querystring.update(kwargs)
        response = requests.post(url, headers=self.headers, json=self.querystring)
        response.raise_for_status()
        response_json = response.json()

        sentencelabel_list = []
        for sentencelabel_dict in response_json:
            sentencelabel = SentenceLabel(
                id_=sentencelabel_dict.get('id'),
                created_at=string_to_date(sentencelabel_dict.get('created_at')),
                updated_at=string_to_date(sentencelabel_dict.get('updated_at')),
                translation=sentencelabel_dict.get('translation'),
                memorialized=sentencelabel_dict.get('memorialized'),
                pagesection=entity.pagesection,
                sentencetranslation=SentenceTranslation(id_=sentencelabel_dict.get('sentence_translation'))
            )
            sentencelabel_list.append(sentencelabel)
        return sentencelabel_list

    def update(self, entity: SentenceLabel) -> SentenceLabel:
        pass

    def remove(self, entity: SentenceLabel) -> bool:
        pass

    
