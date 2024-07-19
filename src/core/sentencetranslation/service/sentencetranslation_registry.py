from uuid import uuid4
from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencetranslation import SentenceTranslation
from .sentencetranslation_repository import SentenceTranslationRepository


@usecase_map('/sentencetranslation/registry')
class SentenceTranslationRegistryService(UseCase):

    def __init__(self, repository: SentenceTranslationRepository):
        self.repository = repository

    def execute(self, entity: SentenceTranslation) -> Result:
        result = Result()
        sentencetranslation = entity.clone()
        
        try:
            new_sentencetranslation = self.repository.registry(sentencetranslation)
            result.entities = new_sentencetranslation
        except Exception as error:
            sentencetranslation_filter = SentenceTranslation(foreign_language=entity.foreign_language)
            has_sentencetranslations = self.repository.find_by_field(sentencetranslation_filter)
            if not has_sentencetranslations:
                result.error_msg = (f'SentenceTranslationRegistryService error: The '
                                    f'sentence="{entity.foreign_language}" was not '
                                    f'created or found in the database.')
                return result
            result.entities = has_sentencetranslations

        return result