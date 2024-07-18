from src.core import usecase_map
from src.core.sentencelabel import SentenceLabel, SentenceLabelFindByField
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/find_by_field')
class PageSectionFindByField(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        
        result = Result()

        try:
            pagesection_list = self.repository.find_by_field(entity)
            
            from src.core.notebook import NotebookFindByFieldService
            from src.external.persistence.djangoapi import ApiNotebookRepository, ApiSentenceLabelRepository
            nt_find_by_field_service = NotebookFindByFieldService(repository=ApiNotebookRepository())
            sl_find_by_field_service = SentenceLabelFindByField(repository=ApiSentenceLabelRepository())
            
            for ps in pagesection_list:
                sl_filter = SentenceLabel(pagesection=ps)
                resp = sl_find_by_field_service.execute(sl_filter).to_dict()

                sl_list = resp.get('entities')
                ps.sentencelabels = sl_list

                messages = resp.get('messages')
                result.error_msg = messages.get('error')

                if not entity.notebook:
                    resp = nt_find_by_field_service.execute(ps.notebook).to_dict()
                    nt_list = resp.get('entities')

                    messages = resp.get('messages')
                    result.error_msg = messages.get('error')

                    if nt_list:
                        ps.notebook = nt_list[-1]
                    else:
                        result.error_msg = (f'PageSectionFindByField service error: '
                                            f'Notebook(id_={ps.notebook.id}) not found error')
            
            result.entities = pagesection_list
        except Exception as error:
            result.error_msg = f'PageSectionFindByField service error: >>> {str(error)}'
            return result 

        return result