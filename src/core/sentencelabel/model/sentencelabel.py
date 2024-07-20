import datetime

from src.core.shared.entity import Entity
from src.core.shared.utils import date_to_string
from src.core.sentencetranslation import SentenceTranslation

class SentenceLabel(Entity):
    def __init__(self, *,
                 id_                 : str=None,
                 created_at          : datetime.date=None,
                 updated_at          : datetime.date=None,
                 sentencetranslation : SentenceTranslation=None,
                 pagesection        : 'PageSection'=None, # type: ignore
                 translation         : str=None,
                 memorialized        : bool=None
                 ):
        self.id                   = id_
        self.created_at           = created_at
        self.updated_at           = updated_at
        self.sentencetranslation = sentencetranslation
        self.pagesection         = pagesection
        self.translation          = translation
        self.memorialized         = memorialized

    def clone(self): # type: ignore
        return SentenceLabel(
            translation=self.translation,
            memorialized=self.memorialized,
            sentencetranslation=self.sentencetranslation.clone()
        )
        
    def data_to_dataframe(self):
        return [
            {
                'id'                  : self.id,
                'created_at'          : self.created_at,
                'updated_at'          : self.updated_at,
                'sentencetranslation' : self.sentencetranslation.mother_language_sentence,
                'pagesection'         : self.pagesection.id,
                'translation'         : self.translation,
                'memorialized'        : self.memorialized,
            }
        ]
    
    def to_dict_with_prefix(self):
        st_to_dict_with_prefix = self.sentencetranslation
        if self.sentencetranslation:
            st_to_dict_with_prefix = self.sentencetranslation.to_dict_with_prefix()
        return {
            'sentencelabel_id_'                 : self.id,
            'sentencelabel_created_at'          : self.created_at,
            'sentencelabel_updated_at'          : self.updated_at,
            'sentencelabel_translation'         : self.translation,
            'sentencelabel_memorialized'        : self.memorialized,
            'sentencelabel_sentencetranslation' : st_to_dict_with_prefix
        }

    def to_dict(self):
        sentencetranslation_id = None
        pagesection_id = None
        if self.sentencetranslation:
            sentencetranslation_id = self.sentencetranslation.id
        if self.pagesection:
            pagesection_id = self.pagesection.id
        return {
            'id'                     : self.id,
            'created_at'             : date_to_string(self.created_at),
            'updated_at'             : date_to_string(self.updated_at),
            'sentencetranslation_id' : sentencetranslation_id,
            'pagesection_id'         : pagesection_id,
            'translation'            : self.translation,
            'memorialized'           : self.memorialized,
        }
    
    def __repr__(self):
        return (
            f'SentenceLabel('
                f'id_={self.id}, '
                f'created_at={self.created_at}, '
                f'updated_at={self.updated_at}, '
                f'sentencetranslation={self.sentencetranslation}, '
                f'pagesection={self.pagesection}, '
                f'translation={self.translation}, '
                f'memorialized={self.memorialized}'
            f')'
        )
    
    def validate(self):
        messages = []

        return messages