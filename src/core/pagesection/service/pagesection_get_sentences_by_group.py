from src.core import usecase_map
from src.core.shared.application import Result
from src.core.shared.usecase import UseCase

from ..model.pagesection import PageSection
from .pagesection_repository import PageSectionRepository


@usecase_map('pagesection/get_sentences_by_group')
class GetSentencesByGroup(UseCase):

    def __init__(self, repository: PageSectionRepository):
        self.repository = repository

    def execute(self, entity: PageSection) -> Result:
        result = Result()

        try:
            sentence_list = self.repository.get_sentences_by_group(entity)
            
            if len(sentence_list) < 1:
                result.info_msg = 'There are no sentences to insert automaticly'
            
            result.entities = sentence_list
            return result

        except Exception as error:
            result.error_msg = str(f'GetSentencesByGroupError: {error}')
            result.entities = entity
            return result