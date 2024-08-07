from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencelabel import SentenceLabel
from .sentencelabel_repository import SentenceLabelRepository


@usecase_map('/sentencelabel/remove')
class SentenceLabelRemove(UseCase):

    def __init__(self, repository: SentenceLabelRepository):
        self.repository = repository

    def execute(self, entity: SentenceLabel) -> Result:
        
        result = Result()        
        result.error_msg = 'SentenceLabelRemove service is not implemented.'
        return result