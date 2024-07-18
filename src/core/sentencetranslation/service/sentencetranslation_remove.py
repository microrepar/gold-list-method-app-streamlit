from uuid import uuid4
from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencetranslation import SentenceTranslation
from .sentencetranslation_repository import SentenceTranslationRepository


@usecase_map('/sentencetranslation/remove')
class SentenceTranslationRemove(UseCase):

    def __init__(self, repository: SentenceTranslationRepository):
        self.repository = repository

    def execute(self, entity: SentenceTranslation) -> Result:
        
        result = Result()
        result.error_msg = 'SentenceTranslationRemove service is not implemented.'
        return result