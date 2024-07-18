from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.sentencelabel import SentenceLabel
from .sentencelabel_repository import SentenceLabelRepository


@usecase_map('/sentencelabel/update')
class SentenceLabelUpdate(UseCase):

    def __init__(self, repository: SentenceLabelRepository):
        self.repository = repository

    def execute(self, entity: SentenceLabel) -> Result:
        
        result = Result()        

        return result