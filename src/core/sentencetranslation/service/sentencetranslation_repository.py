from abc import abstractmethod
from typing import List, Optional, Protocol, runtime_checkable

from src.core.shared.repository import Repository

from ..model.sentencetranslation import SentenceTranslation


@runtime_checkable
class SentenceTranslationRepository(Repository, Protocol):

    @abstractmethod
    def get_all(self, entity: SentenceTranslation = None) -> List[SentenceTranslation]:
        """Get all registred Sentences in the database
        """

    @abstractmethod
    def registry(self, entity: SentenceTranslation, clone_entity: SentenceTranslation) -> SentenceTranslation :
        """Registry a SentenceTranslation into database 
        """

    @abstractmethod
    def get_by_id(self, entity: SentenceTranslation) -> SentenceTranslation:
        """Get by id a registred SentenceTranslation in the database
        """
    
    @abstractmethod
    def find_by_field(self, entity: SentenceTranslation) -> List[Optional[SentenceTranslation]]:
        """Get by id a registred SentenceTranslation in the database
        """
    
    @abstractmethod
    def remove(self, entity: SentenceTranslation) -> bool:
        """Remove by id a SentenceTranslation in the database
        """