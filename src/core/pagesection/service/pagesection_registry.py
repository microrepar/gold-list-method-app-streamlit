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
            result.entities = entity
            return result        

        new_entity = None
        clone_entity = None
        try:
            if entity.group == Group.A:
                clone_entity = entity.clone()
                clone_entity.distillation_at = entity.created_at
                clone_entity.distillated = True
                for sl in clone_entity.sentencelabels:
                    sl.translation = ''
                    sl.memorialized = False

                clone_entity.id = str(uuid4())
                clone_entity = self.repository.registry(entity=clone_entity)
                
                clone_entity = self.repository.registry_sentencelabels(entity=clone_entity)

            entity.id = str(uuid4())
            new_entity = self.repository.registry(entity=entity)
            was_updated = self.repository.update_sentencelabel(entity=new_entity)
            if not was_updated:
                result.warning_msg = 'There was a problem updating the table associated between PageSection and Sentence'
                
            result.entities = new_entity

        except Exception as error:
            if clone_entity is not None:
                self.repository.remove(clone_entity)
            if new_entity is not None:
                self.repository.remove(new_entity)
            result.error_msg = str(error)
            result.entities = entity
            return result        

        return result