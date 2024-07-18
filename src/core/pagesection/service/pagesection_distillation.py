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

        entity_clone = entity.clone()        
        entity_clone.sentences = [entity.sentences[i] for i, m in enumerate(entity.memorializeds) if m is False]
        entity_clone.translated_sentences = ['' for _ in entity_clone.sentences]
        entity_clone.memorializeds = [False for _ in entity_clone.sentences]
        entity_clone.group = NEXT_GROUP.get(entity.group.value)
        entity_clone.set_created_by(entity)
        entity_clone.set_distillation_at()
        
        result.error_msg = entity_clone.validate()
        if entity_clone.group is None:
            result.error_msg = f'Not exists Group {entity.group}'

        entity.distillated = True
        result.error_msg = entity.validate()

        if result.qty_msg() > 0:
            result.entities = entity
            return result

        try:
            updated_pagesection = self.repository.update(entity)
            result.entities = updated_pagesection
            
            new_entity = self.repository.registry(entity_clone)
            
            return result        
        except Exception as error:
            result.error_msg = str(error)
            entity.distillated = None
            result.entities = entity
            
        return result        
        