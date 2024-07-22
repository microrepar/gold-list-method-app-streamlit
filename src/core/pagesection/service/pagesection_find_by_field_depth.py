from src.core import usecase_map
from src.core.sentencelabel import SentenceLabel, SentenceLabelFindByField
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/find_by_field/depth')
class PageSectionFindByFieldDepthService(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        
        result = Result()

        try:
            pagesection_list = self.repository.find_by_field_depth(entity)
            result.entities = pagesection_list
        except Exception as error:
            result.error_msg = f'PageSectionFindByFieldDepthService error: >>> {str(error)}'
            return result 

        return result