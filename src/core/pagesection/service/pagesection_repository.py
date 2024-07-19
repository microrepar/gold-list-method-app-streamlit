from abc import abstractmethod
from typing import List, Optional, Protocol, runtime_checkable

from src.core.shared.repository import Repository

from ..model.pagesection import PageSection


@runtime_checkable
class PageSectionRepository(Repository, Protocol):

    @abstractmethod
    def registry(self, entity: PageSection) -> PageSection:
        """Registry a PageSection into database 
        """

    @abstractmethod
    def get_all(self, entity: PageSection = None) -> List[PageSection]:
        """Get all registred PageSections in database
        """

    @abstractmethod
    def get_by_id(self, entity: PageSection) -> PageSection:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def find_by_field(self, entity: PageSection) -> List[Optional[PageSection]]:
        """Get by id a registred PageSection in database
        """
    
    @abstractmethod
    def get_last_page_number(self, entity: PageSection) -> int:
        """Get next page number to PageSection
        """
    
    @abstractmethod
    def get_sentences_by_group(self, entity: 'SentenceTranslation') -> List['SentenceTranslation']:
        """Get sentences by group
        """
    
    @abstractmethod
    def update(self, entity: PageSection) -> PageSection:
        """Update page number in database
        """
    
    @abstractmethod
    def update_sentencelabel(self, entity: PageSection) -> PageSection:
        """Update associated sentencelabel into table in database
        """
    
    @abstractmethod
    def validate_sentences(self, entity: PageSection) -> List[str]:
        """Validate registred sentences 
        """
    
    @abstractmethod
    def remove(self, entity: PageSection):
        """Remove PageSection by id 
        """

    