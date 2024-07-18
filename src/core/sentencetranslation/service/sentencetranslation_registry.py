from uuid import uuid4
from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencetranslation import SentenceTranslation
from .sentencetranslation_repository import SentenceTranslationRepository


@usecase_map('/sentencetranslation/registry')
class SentenceTranslationRegistry(UseCase):

    def __init__(self, repository: SentenceTranslationRepository):
        self.repository = repository

    def execute(self, entity: SentenceTranslation) -> Result:
        
        result = Result()        

        sentencetranslation_filter = SentenceTranslation(foreign_language=entity.foreign_language)

        has_sentencetranslations = self.repository.find_by_field(sentencetranslation_filter)
        
        if has_sentencetranslations:
            result.entities = has_sentencetranslations
            return result
        
        sentencetranslation = entity.clone()
        
        try:
            new_sentencetranslation = self.repository.registry(sentencetranslation)
            result.entities = new_sentencetranslation
            return result
        
        except Exception as error:
            result.error_msg = str(error)
            result.entities = entity
            return result        
