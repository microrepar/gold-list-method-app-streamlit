from uuid import uuid4

from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import Group, PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('/pagesection/registry')
class PageSectionRegistry(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        
        result = Result()
        
        pagesection_filter = PageSection(created_at=entity.created_at,
                                         group=entity.group,
                                         notebook=entity.notebook)
        has_pagesection = self.repository.find_by_field(pagesection_filter)

        if has_pagesection:
            result.error_msg = (f'Headlist cannot be registred because '
                          f'there is a headlist created at same date {entity.created_at}.')

        next_page_number = self.repository.get_last_page_number(entity) + 1
        entity.page_number = next_page_number
        entity.set_distillation_at()        
        
        result.error_msg = self.repository.validate_sentences(entity)
        result.error_msg = entity.validate()

        if result.qty_msg() > 0:
            return result        

        new_entity = None
        clone_entity = None
        
        from src.core.sentencelabel import SentenceLabelRegistryService
        from src.external.persistence.djangoapi import ApiSentenceLabelRepository
        sl_registry_service = SentenceLabelRegistryService(ApiSentenceLabelRepository())

        try:
            if entity.group == Group.A:
                clone_entity = entity.clone()
                clone_entity.notebook = entity.notebook
                clone_entity.sentencelabels = [sl.clone() for sl in entity.sentencelabels]
                clone_entity.distillation_at = clone_entity.created_at
                clone_entity.distillation_actual = clone_entity.created_at

                clone_entity.distillated = True
                
                clone_entity = self.repository.registry(entity=clone_entity)
                
                sentencelabel_list = []
                for sl in clone_entity.sentencelabels:
                    sl.pagesection = clone_entity
                    sl.memorialized = False
                    sl.translation = ''

                    resp = sl_registry_service.execute(sl).to_dict()

                    entities = resp.get('entities')
                    sentencelabel_list += entities
                    
                    messages = resp.get('messages')
                    result.update_messages(messages)

                    if 'error' in messages:
                        self.repository.remove(clone_entity)
                        return result
                clone_entity.sentencelabels = sentencelabel_list
            
            new_entity = self.repository.registry(entity=entity)
            
            sentencelabel_list = []
            for sl in clone_entity.sentencelabels:
                sl.pagesection = new_entity

                resp = sl_registry_service.execute(sl).to_dict()

                entities = resp.get('entities')
                sentencelabel_list += entities
                
                messages = resp.get('messages')
                result.update_messages(messages)

                if 'error' in messages:
                    self.repository.remove(clone_entity)
                    self.repository.remove(new_entity)
                    return result                
            new_entity.sentencelabels = sentencelabel_list

        except Exception as error:
            if clone_entity is not None:
                self.repository.remove(clone_entity)
            if new_entity is not None:
                self.repository.remove(new_entity)
            result.error_msg = str(error)
            result.entities = entity
            return result        

        result.entities = new_entity
        return result