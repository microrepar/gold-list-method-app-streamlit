import datetime
from enum import Enum
from typing import List

from src.core.notebook import Notebook
from src.core.shared.entity import Entity
from src.core.shared.utils import date_to_string
from src.core.sentencelabel import SentenceLabel


class Group(Enum):
    HEADLIST = 'A'
    A        = 'A'
    B        = 'B'
    C        = 'C'
    D        = 'D'
    NEW_PAGE = 'NP'
    NP       = 'NP'
    REMOVED  = 'RM'

SEQUENCE_GROUP = {
    'A'  : '1st headlist',
    'B'  : '2nd distillation',
    'C'  : '3rd distillation',
    'D'  : '4th distillation',
    'NP' : '🔁 repet headlist'
}

AFTER_SEQUENCE_GROUP = {
    'B'  : ' of A',
    'C'  : ' of B',
    'D'  : ' of C',
    'NP' : ' of D'
}

DIST_GROUP_COLOR = {
    'A'  : '#9B9B9B',
    'B'  : '#9B9B9B',
    'H'  : '#9B9B9B',
    'C'  : '#9B9B9B',
    'D'  : '#9B9B9B',
    'NP' : '#9B9B9B'
}

GROUP_COLOR = {
    'A'  : '#FF0000',
    'B'  : '#00A81D',
    'C'  : '#002BFF',
    'D'  : '#B300B7',
    'NP' : '#000000'
}

GROUP_LABEL = {
    'A'  : 'HeadList',
    'B'  : 'Group B List',
    'C'  : 'Group C List',
    'D'  : 'Group D List',
    'NP' : 'Group NP List'
}


class PageSection(Entity):
    def __init__(self, *,
                 id_                  : str=None,
                 created_at           : datetime.date=None,
                 updated_at           : datetime.date=None,
                 notebook             : Notebook=None,
                 page_number          : int=None,
                 group                : Group=None,
                 distillation_at      : datetime.date=None,
                 distillated          : bool=False,
                 distillation_actual  : datetime.date=None,
                 created_by           : 'PageSection'=None,
                 sentencelabels      : List[SentenceLabel]=[]
            ):
                
        self.id                  = id_
        self.created_at          = created_at
        self.updated_at          = updated_at
        self.notebook            = notebook
        self.page_number         = page_number
        self.group               = group
        self.distillation_at     = distillation_at
        self._distillated        = distillated
        self.distillation_actual = distillation_actual
        self.sentencelabels      = sentencelabels
        self.created_by          = created_by
    
    def clone(self):
        return PageSection(
            id_=self.id,
            created_at=self.created_at,
            updated_at=self.updated_at,
            page_number=self.page_number,
            group=self.group,
            distillation_at=self.distillation_at,
            distillated=self.distillated,
            distillation_actual=self.distillation_actual,
        )
    
    @property
    def distillated(self):
        return self._distillated

    @distillated.setter
    def distillated(self, value: bool) :
        if value:
            self._distillated = True
            self.distillation_actual = datetime.datetime.now().date()
        else:
            self._distillated = False
            self.distillation_actual = None

    def set_id(self, id_):
        self.id = id_

    def __str__(self):        
        notebook_value = self.notebook.name if isinstance(self.notebook, Notebook) else ''
        return (f'{GROUP_LABEL.get(self.group.value)} Page {self.page_number} of {self.created_at} with '
                f'distillation date of {self.distillation_at} from the {notebook_value} notebook') if self.group != Group.NEW_PAGE \
                else f'{GROUP_LABEL.get(self.group.value)} of {self.created_at} will be able to composite a new HeadList.'
        
    def __repr__(self):
        created_by_id = self.created_by
        if self.created_by is not None:
            created_by_id = self.created_by.id
        notebook_id = None
        if self.notebook is not None:
            notebook_id = self.notebook.id
        return (f'PageSection('
                    f'id_= {self.id}, '
                    f'page_number={self.page_number}, '
                    f'created_at={self.created_at}, '
                    f'created_by_id={created_by_id}, '
                    f'notebook_id={notebook_id}, '
                    f'group="{self.group}", '
                    f'distillated={self.distillated}'
                ')'
        )
    
    def get_distillation_event(self):
        if self.distillated:
            color = DIST_GROUP_COLOR
        else:
            color = GROUP_COLOR
        return {
            "title"      : (f"{self.group.value}{self.page_number} ({SEQUENCE_GROUP.get(self.group.value, 'Indef')}"
                            f"{AFTER_SEQUENCE_GROUP.get(self.group.value, '')})") \
                                if (self.created_at != self.distillation_at) else f"🗣️ {self.group.value}{self.page_number} Add HeadList",
            "color"      : color.get(self.group.value, color['NP']) if self.created_at \
                            else '#DCDCDC',
            "start"      : f"{self.distillation_at}",
            "end"        : f"{self.distillation_at}",
            "resourceId" : f"{self.group.value.lower()}",
        }
    
    def get_columns_from_dataframe(self):
        return [
            # 'Page section id',
            # 'notebook_id',
            # 'updated_at',
            'notebook_name',
            'page',
            'group',
            'created_at',
            'distillation_at',
            'distillated',
            'distillation_actual',
            'created_by_id',
        ]

    def data_to_dataframe(self):
        created_by_id = self.created_by
        if self.created_by is not None:
            created_by_id = self.created_by.page_number
        return [{    
            'Page section id'                  : self.id,
            'page'                : self.page_number,
            'group'               : self.group.value,
            'created_at'          : self.created_at,
            'updated_at'          : self.updated_at,
            'created_by_id'       : created_by_id,
            'distillation_at'     : self.distillation_at,
            'distillation_actual' : self.distillation_actual,
            'distillated'         : self._distillated,
            'notebook_id'         : self.notebook.id,
            'notebook_name'       : self.notebook.name,
        }]
    
    def to_dict(self):
        created_by_id = self.created_by
        notebook_id = self.notebook
        group_value = self.group
        if self.created_by is not None:
            created_by_id = self.created_by.id
        if self.notebook:
            notebook_id = self.notebook.id
        if self.group:
            group_value = self.group.value
        return {    
            'id'                  : self.id,
            'created_at'          : date_to_string(self.created_at),
            'updated_at'          : date_to_string(self.updated_at),
            'page_number'         : self.page_number,
            'group'               : group_value,
            'distillated'         : self._distillated,
            'distillation_at'     : date_to_string(self.distillation_at),
            'distillation_actual' : date_to_string(self.distillation_actual),
            'notebook_id'         : notebook_id,
            'created_by_id'       : created_by_id,
        }
    
    def to_dict_with_prefix(self):
        return {    
            'id'                  : self.id,
            'created_at'          : self.created_at,
            'updated_at'          : self.updated_at,
            'page_number'         : self.page_number,
            'group'               : self.group.value,
            'distillated'         : self._distillated,
            'distillation_at'     : self.distillation_at,
            'distillation_actual' : self.distillation_actual,
        }

    def validate(self):
        messages = []
        if self.notebook is None or self.notebook.days_period is None:
            messages.append(f'Notebook is none or it has not defined days_period attribute value.')
        
        empty_sentences = 0
        repeated_counter = dict()

        
        for sentencelabel in self.sentencelabels:            
            if sentencelabel.sentencetranslation.foreign_language == '' \
                    or sentencelabel.sentencetranslation.mother_tongue == '' \
                    or sentencelabel.sentencetranslation.foreign_language is None \
                    or sentencelabel.sentencetranslation.mother_tongue is None:
                empty_sentences += 1

            repeated_counter.setdefault(sentencelabel.sentencetranslation.foreign_language, 0)
            repeated_counter[sentencelabel.sentencetranslation.foreign_language] += 1
        
        if empty_sentences > 0:
            messages.append('There is one or more empty fields to headlist. Fill the gaps and try again.')
            return messages
                
        for k, v in repeated_counter.items():
            if v > 1:
                messages.append(f'This sentence="{k}" is repeated into Headlist')
        
        if messages:
            return messages

    def set_distillation_at(self):
        self.distillation_at = (self.created_at + datetime.timedelta(days=self.notebook.days_period))

                