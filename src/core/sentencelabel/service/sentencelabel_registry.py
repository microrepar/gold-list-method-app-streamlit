from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencelabel import SentenceLabel
from .sentencelabel_repository import SentenceLabelRepository


@usecase_map('/sentencelabel/registry')
class SentenceLabelRegistryService(UseCase):

    def __init__(self, repository: SentenceLabelRepository):
        self.repository = repository

    def execute(self, entity: SentenceLabel) -> Result:
        
        result = Result()

        from src.core.sentencetranslation import SentenceTranslationRegistryService                                                  
        from src.external.persistence.djangoapi import ApiSentenceTranslationRepository
        st_registry_service = SentenceTranslationRegistryService(ApiSentenceTranslationRepository())

        resp = st_registry_service.execute(entity.sentencetranslation).to_dict()
        
        entities = resp.get('entities')
        messages = resp.get('messages')
        result.update_messages(messages)

        if 'error' in messages:
            result.error_msg = (f'SentenceLabelRegistryService error:  '
                                f'No sentence labels registred to {entity}')
            return result
            
        sentencetranslation = entities[-1]
        entity.sentencetranslation = sentencetranslation
            
        try:
            new_sentencelabel: SentenceLabel = self.repository.registry(entity)
            result.entities = new_sentencelabel

        except Exception as error:
            error_msg = ('SentenceLabelRegistryService error: An error occurred while '
                         f'registering the SentenceLabel ->>> {str(error)}')
            result.error_msg = error_msg
            return result

        return result