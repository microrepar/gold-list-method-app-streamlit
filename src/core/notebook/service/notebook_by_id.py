from typing import List

from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result

from .. import Notebook, NotebookRepository


@usecase_map('/notebook/id')
class NotebookGetById(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        result = Result()
        has_notebook = self.repository.get_by_id(notebook)

        if not has_notebook:
            result.error_msg = f'There are no registred notebooks!'
            result.entities = notebook
            return result
        
        result.entities = has_notebook
        return result
