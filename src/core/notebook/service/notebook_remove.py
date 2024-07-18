from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository


class NotebookRemoveService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, notebook: Notebook) -> Result:
        """return super().execute(notebook)"""