from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ... import usecase_map
from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/remove')
class PageSectionRemove(UseCase):

    def __init__(self, repository: PageSectionRepository):
        
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()
        result.error_msg = 'PageSectionRemove service is not implemented.'
        return result        
        