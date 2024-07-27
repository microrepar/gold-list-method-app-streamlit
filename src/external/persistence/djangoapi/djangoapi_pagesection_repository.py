import datetime
from typing import List

import requests

from config import Config
from src.core.notebook import Notebook
from src.core.pagesection import Group, PageSection, PageSectionRepository
from src.core.sentencelabel import SentenceLabel
from src.core.sentencetranslation import SentenceTranslation
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
        pagesection_dict = {k: v for k, v in pagesection_dict.items() if v is not None}

        response = requests.post(url, headers=self.headers, json=pagesection_dict)
        response.raise_for_status()
        response_json = response.json()
        
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
    
    def registry_depth(self, entity: PageSection) -> PageSection:
        url = self.url + 'depth/'
        pagesection_dict = entity.to_dict()
        pagesection_dict.pop('id')
        pagesection_dict.pop('updated_at')
        pagesection_dict['sentencelabels'] = [sl.to_dict() for sl in entity.sentencelabels]
        for sl_dict in pagesection_dict['sentencelabels']:
            sl_dict.pop('id')
            sl_dict.pop('updated_at')
            sl_dict.pop('created_at')
            sl_dict.pop('pagesection_id')
            sl_dict = {k: v for k, v in sl_dict.items() if v}
            sl_dict['sentencetranslation'].pop('id')
            sl_dict['sentencetranslation'].pop('created_at')
            sl_dict['sentencetranslation'].pop('updated_at')
            sl_dict['sentencetranslation'] = {k: v for k, v in sl_dict['sentencetranslation'].items() if v}
        pagesection_dict = {k: v for k, v in pagesection_dict.items() if v}
        
        response = requests.post(url, headers=self.headers, json=pagesection_dict)
        response.raise_for_status()
        pagesection_dict = response.json()

        sl_list = []
        for sentencelabel_dict in pagesection_dict.get('sentencelabels'):
            sentencelabel = SentenceLabel(
                id_=sentencelabel_dict.get('id'),
                created_at=string_to_date(sentencelabel_dict.get('created_at')),
                updated_at=string_to_date(sentencelabel_dict.get('updated_at')),
                pagesection=PageSection(
                    id_=pagesection_dict.get('id'),
                    created_at=string_to_date(pagesection_dict.get('created_at')),
                    page_number=pagesection_dict.get('page_number'),
                    group=Group[pagesection_dict.get('group')],
                    distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
                    distillated=pagesection_dict.get('distillated'),
                    distillation_actual=pagesection_dict.get('distillation_actual')
                ),
                translation=sentencelabel_dict.get('translation'),
                memorialized=sentencelabel_dict.get('memorialized')
            )
            sentencetranslation_dict = sentencelabel_dict.get('sentencetranslation')
            sentencetranslation = SentenceTranslation(
                id_=sentencetranslation_dict.get('id'),
                created_at=string_to_date(sentencetranslation_dict.get('created_at')),
                updated_at=string_to_date(sentencetranslation_dict.get('updated_at')),
                foreign_language=sentencetranslation_dict.get('foreign_language_sentence'),
                mother_tongue=sentencetranslation_dict.get('mother_language_sentence'),
                foreign_idiom=sentencetranslation_dict.get('foreign_language_idiom'),
                mother_idiom=sentencetranslation_dict.get('mother_language_idiom')
            )
            sentencelabel.sentencetranslation = sentencetranslation
            sl_list.append(sentencelabel)

        notebook_dict = pagesection_dict.get('notebook')
        notebook = Notebook(
            id_=notebook_dict.get('id'),
            name=notebook_dict.get('name'),
            created_at=string_to_date(notebook_dict.get('created_at')),
            updated_at=string_to_date(notebook_dict.get('updated_at')),
            sentence_list_size=[],
            days_period=notebook_dict.get('days_period'),
            foreign_idiom=notebook_dict.get('foreign_idiom'),
            mother_idiom=notebook_dict.get('mother_idiom'),
        )

        created_by = None
        created_by_dict = pagesection_dict.get('created_by')
        if created_by_dict:
            created_by = PageSection(
                id_=created_by_dict.get('id'),
                created_at=string_to_date(created_by_dict.get('created_at')),
                sentencelabels=[],
                page_number=created_by_dict.get('page_number'),
                group=Group[created_by_dict.get('group')],
                distillation_at=string_to_date(created_by_dict.get('distillation_at')),
                distillated=created_by_dict.get('distillated'),
                distillation_actual=created_by_dict.get('distillation_actual')
            )

        pagesection = PageSection(
            id_=pagesection_dict.get('id'),
            created_at=string_to_date(pagesection_dict.get('created_at')),
            created_by=created_by,
            notebook=notebook,
            sentencelabels=sl_list,
            page_number=pagesection_dict.get('page_number'),
            group=Group[pagesection_dict.get('group')],
            distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
            distillated=pagesection_dict.get('distillated'),
            distillation_actual=pagesection_dict.get('distillation_actual')
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

        response = requests.put(url, headers=self.headers, json=pagesection_dict)
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
    
    def update_depth(self, entity: PageSection) -> PageSection:
        url = self.url + f'depth/{entity.id}'
        pagesection_dict = entity.to_dict()
        pagesection_dict.pop('id')
        pagesection_dict.pop('created_at')
        pagesection_dict.pop('updated_at')
        pagesection_dict['sentencelabels'] = [sl.to_dict() for sl in entity.sentencelabels]
        for sl_dict in pagesection_dict['sentencelabels']:
            sl_dict.pop('created_at')
            sl_dict.pop('updated_at')
            sl_dict = {k: v for k, v in sl_dict.items() if v}
        pagesection_dict = {k: v for k, v in pagesection_dict.items() if v}

        response = requests.put(url, headers=self.headers, json=pagesection_dict)
        response.raise_for_status()
        pagesection_dict = response.json()
        
        sl_list = []
        for sentencelabel_dict in pagesection_dict.get('sentencelabels'):
            sentencelabel = SentenceLabel(
                id_=sentencelabel_dict.get('id'),
                created_at=string_to_date(sentencelabel_dict.get('created_at')),
                updated_at=string_to_date(sentencelabel_dict.get('updated_at')),
                pagesection=PageSection(
                    id_=pagesection_dict.get('id'),
                    created_at=string_to_date(pagesection_dict.get('created_at')),
                    page_number=pagesection_dict.get('page_number'),
                    group=Group[pagesection_dict.get('group')],
                    distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
                    distillated=pagesection_dict.get('distillated'),
                    distillation_actual=pagesection_dict.get('distillation_actual')
                ),
                translation=sentencelabel_dict.get('translation'),
                memorialized=sentencelabel_dict.get('memorialized')
            )
            sentencetranslation_dict = sentencelabel_dict.get('sentencetranslation')
            sentencetranslation = SentenceTranslation(
                id_=sentencetranslation_dict.get('id'),
                created_at=string_to_date(sentencetranslation_dict.get('created_at')),
                updated_at=string_to_date(sentencetranslation_dict.get('updated_at')),
                foreign_language=sentencetranslation_dict.get('foreign_language_sentence'),
                mother_tongue=sentencetranslation_dict.get('mother_language_sentence'),
                foreign_idiom=sentencetranslation_dict.get('foreign_language_idiom'),
                mother_idiom=sentencetranslation_dict.get('mother_language_idiom')
            )
            sentencelabel.sentencetranslation = sentencetranslation
            sl_list.append(sentencelabel)

        notebook_dict = pagesection_dict.get('notebook')
        notebook = Notebook(
            id_=notebook_dict.get('id'),
            name=notebook_dict.get('name'),
            created_at=string_to_date(notebook_dict.get('created_at')),
            updated_at=string_to_date(notebook_dict.get('updated_at')),
            sentence_list_size=[],
            days_period=notebook_dict.get('days_period'),
            foreign_idiom=notebook_dict.get('foreign_idiom'),
            mother_idiom=notebook_dict.get('mother_idiom'),
        )

        created_by = None
        created_by_dict = pagesection_dict.get('created_by')
        if created_by_dict:
            created_by = PageSection(
                id_=created_by_dict.get('id'),
                created_at=string_to_date(created_by_dict.get('created_at')),
                sentencelabels=[],
                page_number=created_by_dict.get('page_number'),
                group=Group[created_by_dict.get('group')],
                distillation_at=string_to_date(created_by_dict.get('distillation_at')),
                distillated=created_by_dict.get('distillated'),
                distillation_actual=created_by_dict.get('distillation_actual')
            )

        pagesection = PageSection(
            id_=pagesection_dict.get('id'),
            created_at=string_to_date(pagesection_dict.get('created_at')),
            created_by=created_by,
            notebook=notebook,
            sentencelabels=sl_list,
            page_number=pagesection_dict.get('page_number'),
            group=Group[pagesection_dict.get('group')],
            distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
            distillated=pagesection_dict.get('distillated'),
            distillation_actual=pagesection_dict.get('distillation_actual')
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
        
        response = requests.post(url, headers=self.headers, json=kwargs)
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
    
    def find_by_field_clean(self, entity: PageSection) -> List[PageSection]:
        return []
    
    def find_by_field_depth(self, entity: PageSection) -> List[PageSection]:
        url = self.url + f'find_by_field/depth/'
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
        
        response = requests.post(url, headers=self.headers, json=kwargs)
        response.raise_for_status()
        response_json = response.json()

        pagesection_list = []
        for pagesection_dict in response_json:
            sl_list = []
            for sentencelabel_dict in pagesection_dict.get('sentencelabels'):
                sentencelabel = SentenceLabel(
                    id_=sentencelabel_dict.get('id'),
                    created_at=string_to_date(sentencelabel_dict.get('created_at')),
                    updated_at=string_to_date(sentencelabel_dict.get('updated_at')),
                    pagesection=sentencelabel_dict.get('pagesection'),
                    translation=sentencelabel_dict.get('translation'),
                    memorialized=sentencelabel_dict.get('memorialized')
                )
                sentencetranslation_dict = sentencelabel_dict.get('sentencetranslation')
                sentencetranslation = SentenceTranslation(
                    id_=sentencetranslation_dict.get('id'),
                    created_at=string_to_date(sentencetranslation_dict.get('created_at')),
                    updated_at=string_to_date(sentencetranslation_dict.get('updated_at')),
                    foreign_language=sentencetranslation_dict.get('foreign_language_sentence'),
                    mother_tongue=sentencetranslation_dict.get('mother_language_sentence'),
                    foreign_idiom=sentencetranslation_dict.get('foreign_language_idiom'),
                    mother_idiom=sentencetranslation_dict.get('mother_language_idiom')
                )
                sentencelabel.sentencetranslation = sentencetranslation
                sl_list.append(sentencelabel)

            notebook_dict = pagesection_dict.get('notebook')
            notebook = Notebook(
                id_=notebook_dict.get('id'),
                name=notebook_dict.get('name'),
                created_at=string_to_date(notebook_dict.get('created_at')),
                updated_at=string_to_date(notebook_dict.get('updated_at')),
                sentence_list_size=[],
                days_period=notebook_dict.get('days_period'),
                foreign_idiom=notebook_dict.get('foreign_idiom'),
                mother_idiom=notebook_dict.get('mother_idiom'),
            )

            created_by = None
            created_by_dict = pagesection_dict.get('created_by')
            if created_by_dict:
                created_by = PageSection(
                    id_=created_by_dict.get('id'),
                    created_at=string_to_date(created_by_dict.get('created_at')),
                    sentencelabels=[],
                    page_number=created_by_dict.get('page_number'),
                    group=Group[created_by_dict.get('group')],
                    distillation_at=string_to_date(created_by_dict.get('distillation_at')),
                    distillated=created_by_dict.get('distillated'),
                    distillation_actual=created_by_dict.get('distillation_actual')
                )

            pagesection = PageSection(
                id_=pagesection_dict.get('id'),
                created_at=string_to_date(pagesection_dict.get('created_at')),
                # created_by=pagesection_dict.get('created_by'),
                # notebook=pagesection_dict.get('notebook'),
                notebook=entity.notebook,
                # sentencelabels=entity.sentencelabels,
                page_number=pagesection_dict.get('page_number'),
                group=Group[pagesection_dict.get('group')],
                distillation_at=string_to_date(pagesection_dict.get('distillation_at')),
                distillated=pagesection_dict.get('distillated'),
                distillation_actual=pagesection_dict.get('distillation_actual')
            )
            pagesection.created_by = created_by
            pagesection.notebook = notebook
            pagesection.sentencelabels = sl_list
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
