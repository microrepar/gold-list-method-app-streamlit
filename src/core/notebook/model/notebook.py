import datetime
from typing import List

from src.core.shared.entity import Entity
from src.core.shared.utils import date_to_string
from src.core.user import User


class Notebook(Entity):
    def __init__(self, *,
                 id_                : str = None,
                 name               : str = None,
                 created_at         : datetime.date = None,
                 updated_at         : datetime.date = None,
                 sentence_list_size : int = None,
                 days_period        : int = None,
                 pagesection_list  : List['PageSection'] = list(), # type: ignore
                 foreign_idiom      : str = None,
                 mother_idiom       : str = None,
                 user               : User = None):
        
        self.id                = id_
        self.name              = name
        self.created_at        = created_at
        self.updated_at        = updated_at
        self.sentence_list_size= sentence_list_size
        self.days_period       = days_period
        self.pagesection_list = pagesection_list
        self.foreign_idiom     = foreign_idiom
        self.mother_idiom      = mother_idiom
        self.user              = user

    def validate(self) -> List[str]:
        
        msg  = list()
        if not self.name or self.name.strip() == '':
            msg.append(
                'Field "name" cannot empty or filled with white spaces.'
            )
        if not self.foreign_idiom or self.foreign_idiom.strip() == '':
            msg.append(
                'Field "foreign idiom" cannot empty or filled with white spaces.'
            )
        if not self.mother_idiom or self.mother_idiom.strip() == '':
            msg.append(
                'Field "mother idiom" cannot empty or filled with white spaces.'
            )
        return msg
    
    def get_columns_from_dataframe(self):
        return [
            # 'Id', 
            'Name', 
            'Created at', 
            'Updated at', 
            'List size', 
            'Period', 
            'Foreign idiom', 
            'mother_idiom', 
            'User id',
        ]

    def data_to_dataframe(self):
        user_id = None
        if self.user is not None:
            user_id = self.user.id
        return [
            {
                'Id': self.id,
                'Name': self.name,
                'Created at': self.created_at,
                'Updated at': self.updated_at,
                'List size': self.sentence_list_size,
                'Period': self.days_period,
                'Foreign idiom': self.foreign_idiom,
                'mother_idiom': self.mother_idiom,
                'User id': user_id
            }
        ]
    
    def to_dict(self):
        return {
                'id'                 : self.id,
                'name'               : self.name,
                'created_at'         : date_to_string(self.created_at),
                'updated_at'         : date_to_string(self.updated_at),
                'sentence_list_size' : self.sentence_list_size,
                'days_period'        : self.days_period,
                'foreign_idiom'      : self.foreign_idiom,
                'mother_idiom'       : self.mother_idiom,
                'user_id'            : self.user.id,
            }
    
    def to_dict_with_prefix(self):
        return {
                'notebook_id_'                : self.id,
                'notebook_name'               : self.name,
                'notebook_created_at'         : self.created_at,
                'notebook_updated_at'         : self.updated_at,
                'notebook_sentence_list_size' : self.sentence_list_size,
                'notebook_days_period'        : self.days_period,
                'notebook_foreign_idiom'      : self.foreign_idiom,
                'notebook_mother_idiom'       : self.mother_idiom,
            }
    
    def __str__(self) -> str:
        return (f'{self.__class__.__name__}'
                '('
                    f'id={self.id}, '
                    f'name={self.name}, '
                    f'sentence_list_size={self.sentence_list_size}, '
                    f'days_period={self.days_period}, '
                    f'foreign_idiom={self.foreign_idiom}, '
                    f'mother_idiom={self.mother_idiom},'
                    f'user={self.user}'
                ')'
            )
    
    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}'
                f'('
                    f'id={self.id}, '
                    f'name="{self.name}", '
                    f'sentence_list_size={self.sentence_list_size}, '
                    f'days_period={self.days_period}, '
                    f'foreign_idiom={self.foreign_idiom}, '
                    f'mother_idiom={self.mother_idiom}'
                ')'
        )
    
    def get_pagesection(self, *, distillation_at, group) -> 'PageSection': # type: ignore
        for pagesection in self.pagesection_list:
            if distillation_at == pagesection.distillation_at \
                    and group == pagesection.group \
                        and pagesection.created_at != distillation_at:
                return pagesection
    
    def count_pagesection_by_group(self, *, group):
       return len([p for p in self.pagesection_list if p.group.value == group.value and p.created_at != p.distillation_at])

