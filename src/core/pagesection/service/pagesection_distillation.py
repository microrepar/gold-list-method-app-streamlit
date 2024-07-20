from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import Group, PageSection
from .pagesection_repository import PageSectionRepository

NEXT_GROUP = {
    'A': Group.B,
    'B': Group.C,
    'C': Group.D,
    'D': Group.NEW_PAGE,
}


@usecase_map('/pagesection/distillation')
class PageSectionDistillation(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        # Creates clone to registry pagesection with new group
        entity_clone = entity.clone()            
        entity_clone.created_by = entity
        entity_clone.notebook = entity.notebook
        entity_clone.created_at = entity.distillation_actual
        entity_clone.group = NEXT_GROUP.get(entity.group.value)
        entity_clone.set_distillation_at()
        entity_clone.distillation_actual = None
        entity_clone.sentencelabels = [sl.clone() for sl in entity.sentencelabels if sl.memorialized is False]
        for sl in entity_clone.sentencelabels:            
            sl.pagesection = entity_clone
            sl.translation = ''
            sl.memorialized = False
        result.error_msg = entity_clone.validate()
        if entity_clone.group is None:
            result.error_msg = f'Not exists Group {entity.group}'

        entity.distillated = True
        result.error_msg = entity.validate()
        if result.qty_msg() > 0:
            result.entities = entity
            return result

        from src.core.sentencelabel import SentenceLabelRegistryService, SentenceLabelUpdate
        from src.external.persistence.djangoapi import ApiSentenceLabelRepository

        try:
            updated_pagesection = self.repository.update(entity)
            sl_update_service = SentenceLabelUpdate(ApiSentenceLabelRepository())
            sl_list = []
            for sl in entity.sentencelabels:
                resp = sl_update_service.execute(sl).to_dict()
                entities = resp.get('entities')
                messages = resp.get('messages')
                result.update_messages(messages)
                if entities:
                    sl_list.append(entities[-1])
            updated_pagesection.sentencelabels = sl_list
            result.entities = updated_pagesection            

            new_entity = self.repository.registry(entity_clone)            
            sl_registry_service = SentenceLabelRegistryService(ApiSentenceLabelRepository())
            sentencelabel_list = []
            for sl in entity_clone.sentencelabels:
                sl.pagesection = new_entity

                resp = sl_registry_service.execute(sl).to_dict()

                entities = resp.get('entities')
                sentencelabel_list += entities
                
                messages = resp.get('messages')
                result.update_messages(messages)

                if 'error' in messages:                    
                    self.repository.remove(new_entity)
                    return result                
            new_entity.sentencelabels = sentencelabel_list
            
            result.success_msg = f'The distillation was recorded successfully..'
            result.success_msg = f'Sentences not memorized have been moved to {new_entity}.'

        except Exception as error:
            result.error_msg = (f'PageSectionDistillation service error: An error occurred '
                                f'during the distillation recording. >>> {str(error)}')
            entity.distillated = None
            result.entities = entity
            
        return result        
        