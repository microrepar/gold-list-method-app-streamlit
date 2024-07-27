from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ... import usecase_map
from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/update_depth')
class PageSectionUpdateDepthService(UseCase):

    def __init__(self, repository: PageSectionRepository):        
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        try:
            updated_pagesection = self.repository.update_depth(entity)
            result.entities = updated_pagesection
        
        except Exception as error:
            result.error_msg = (f'PageSectionUpdateDepthService service error: An error occurred '
                                f'while updating pagesection id={entity.id}. >>> {str(error)}')
            result.entities = entity
            return result
        
        result.success_msg = 'Translations were updated successfully.'
        return result