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

        sl_list = []
        if entity.sentencelabels:
            from src.core.sentencelabel import SentenceLabelUpdate
            from src.external.persistence.djangoapi import ApiSentenceLabelRepository
            sl_update_service = SentenceLabelUpdate(ApiSentenceLabelRepository())
            for sl in entity.sentencelabels:
                resp = sl_update_service.execute(sl).to_dict()
                entities = resp.get('entities')
                messages = resp.get('messages')
                result.update_messages(messages)
                if entities:
                    sl_list.append(entities[-1])

        try:
            updated_pagesection = self.repository.update(entity)
            updated_pagesection.sentencelabels = sl_list
            result.entities = updated_pagesection
        
        except Exception as error:
            result.error_msg = (f'PageSectionUpdate service error: An error occurred '
                                f'while updating pagesection id={entity.id}. >>> {str(error)}')
            result.entities = entity
            return result
        
        result.success_msg = 'Translations were updated successfully.'
        return result