from typing import List

from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result

from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository


@usecase_map("/notebook/find_by_field_clean")
class NotebookFindByFieldCleanService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, entity: Notebook) -> Result:
        result = Result()
        
        try:
            notebook_list: List[Notebook] = self.repository.find_by_field_clean(entity)
            result.entities = notebook_list
            
            if not notebook_list:
                result.info_msg = f"NotebookFindByFieldCleanService warning: There are no registred notebooks to connected user!"
                result.entities = notebook_list
                return result

        except Exception as error:
            result.error_msg = f'NotebookFindByFieldCleanService service error: An error occurred while querying the database. >>> {str(error)}'
            result.entities = entity
            return result 
        return result
