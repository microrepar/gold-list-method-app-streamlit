from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ... import usecase_map
from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/update')
class PageSectionUpdate(UseCase):

    def __init__(self, repository: PageSectionRepository):
        
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        try:
            updated_pagesection = self.repository.update(entity)
            result.entities = updated_pagesection
            return result
        
        except Exception as error:
            result.error_msg = str(error)
            result.entities = entity
            return result        
        