from uuid import uuid4
from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencetranslation import SentenceTranslation
from .sentencetranslation_repository import SentenceTranslationRepository


@usecase_map('/sentencetranslation/find_by_field')
class SentenceTranslationFindByField(UseCase):

    def __init__(self, repository: SentenceTranslationRepository):
        self.repository = repository

    def execute(self, entity: SentenceTranslation) -> Result:        
        result = Result()
        
        try:                        
            sentencetranslation_list = self.repository.find_by_field(entity)
            result.entities = sentencetranslation_list

        except Exception as error:
            result.error_msg = f'SentenceTranslationFindByField service error: {str(error)}'
            return result

        return result