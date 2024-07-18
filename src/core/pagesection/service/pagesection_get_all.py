from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection')
class PageSectionGetAll(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection=None) -> Result:
        result = Result()

        pagesection_list = self.repository.get_all()

        if len(pagesection_list) == 0:
            result.error_msg = f'There are no page sections into notebook.'
            return result
        
        result.entities = pagesection_list
        
        return result