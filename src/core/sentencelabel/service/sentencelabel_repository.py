from abc import abstractmethod
from typing import List, Protocol, runtime_checkable

from src.core.shared.repository import Repository

from ..model.sentencelabel import SentenceLabel


@runtime_checkable
class SentenceLabelRepository(Repository, Protocol):

    @abstractmethod
    def registry(self, entity: SentenceLabel, clone_entity: SentenceLabel) -> SentenceLabel :
        """Registry a SentenceLabel into database 
        """

    @abstractmethod
    def get_all(self, entity: SentenceLabel = None) -> List[SentenceLabel]:
        """Get all registred Sentences in the database
        """

    @abstractmethod
    def get_by_id(self, entity: SentenceLabel) -> SentenceLabel:
        """Get by id a registred SentenceLabel in the database
        """
    
    @abstractmethod
    def find_by_field(self, entity: SentenceLabel) -> SentenceLabel:
        """Get by id a registred SentenceLabel in the database
        """
    
    @abstractmethod
    def remove(self, entity: SentenceLabel) -> SentenceLabel:
        """Remove by id a SentenceLabel in the database
        """
    