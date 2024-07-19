from typing import List

from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencelabel import SentenceLabel
from .sentencelabel_repository import SentenceLabelRepository


@usecase_map('/sentencelabel/find_by_field')
class SentenceLabelFindByField(UseCase):

    def __init__(self, repository: SentenceLabelRepository):
        self.repository = repository

    def execute(self, entity: SentenceLabel) -> Result:
        
        result = Result()
        
        sl = None
        try:
            sentencelabel_list: List[SentenceLabel] = self.repository.find_by_field(entity)

            if not sentencelabel_list:
                result.error_msg = f'SentenceLabelFindByField service error:  No sentence labels found to {entity}'
                return result
            
            from src.core.sentencetranslation import SentenceTranslationFindByField, SentenceTranslation
            from src.external.persistence.djangoapi import ApiSentenceTranslationRepository
            st_find_by_field = SentenceTranslationFindByField(repository=ApiSentenceTranslationRepository())

            
            for sl in sentencelabel_list:
                st_filter = SentenceTranslation(id_=sl.sentencetranslation.id)
                resp = st_find_by_field.execute(st_filter).to_dict()
                st_list = resp.get('entities')

                messages = resp.get('messages')
                result.error_msg = messages.get('error')
                
                if st_list:
                    sl.sentencetranslation = st_list[-1]
                else:
                    sl.sentencetranslation = None
                    result.error_msg = (f'SentenceLabelFindByField service error:  SentenceLabel(pagesection=PageSection(id_={entity.pagesection.id})) - '
                                        f'SentenceLabel(id_={sl.sentencetranslation}) not found error')
                
            result.entities = sentencelabel_list
        except Exception as error:
            result.error_msg = (f'SentenceLabelFindByField service error: '
                                f'SentenceLabel(id_= {entity.pagesection.id}) - {str(error)}')
            return result 

        return result