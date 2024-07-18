from typing import List

from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result
from .. import Notebook, NotebookRepository


@usecase_map('/notebook')
class NotebookAllService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        result = Result()
        notebook_list = self.repository.get_all()

        if not notebook_list:
            result.error_msg = f'There are no registred notebooks!'
            result.entities = notebook_list
            return result
        
        result.entities = notebook_list
        return result
