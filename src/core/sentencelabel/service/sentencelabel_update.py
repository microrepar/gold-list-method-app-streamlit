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

        try:
            updated_sl = self.repository.update(entity)
            result.entities = updated_sl
        except Exception as error:
            result.error_msg = (f'SentenceLabelUpdate service error: An error occurred '
                                f'while updating SentenceLabel id={entity.id}. >>> {str(error)}')
            result.entities = entity
            return result
        
        return result