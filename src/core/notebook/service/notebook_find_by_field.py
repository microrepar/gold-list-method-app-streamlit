from typing import List

from src.core import usecase_map
from src.core.shared import UseCase
from src.core.shared.application import Result

from ..model.notebook import Notebook
from .notebook_repository import NotebookRepository


@usecase_map("/notebook/find_by_field")
class NotebookFindByFieldService(UseCase):

    def __init__(self, *, repository: NotebookRepository):
        self.repository = repository

    def execute(self, entity: Notebook) -> Result:
        result = Result()
        
        try:
            notebook_list: List[Notebook] = self.repository.find_by_field(entity)
            
            if not notebook_list:
                result.info_msg = f"NotebookFindByFieldService info: There are no registred notebooks to connected user!"
                result.entities = notebook_list
                return result
            # import ipdb; ipdb.set_trace()

            from src.core.pagesection import PageSectionFindByField, PageSection
            from src.external.persistence.djangoapi import ApiPageSectionRepository
            ps_find_by_field_service = PageSectionFindByField(repository=ApiPageSectionRepository())
            
            for nt in notebook_list:
                ps_filter = PageSection(notebook=nt)
                resp = ps_find_by_field_service.execute(ps_filter).to_dict()

                ps_list = resp.get('entities')
                nt.pagesection_list = ps_list
                
                messages = resp.get('messages')
                result.error_msg = messages.get('error')

            result.entities = notebook_list
        except Exception as error:
            result.error_msg = f'NotebookFindByFieldService service error: An error occurred while querying the database. >>> {str(error)}'
            result.entities = entity
            return result 
        return result
