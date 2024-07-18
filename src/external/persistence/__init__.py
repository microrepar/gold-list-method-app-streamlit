
"""persistence module
"""
import os
from importlib import import_module
from pathlib import Path
from typing import List, Protocol

from config import Config
from src.core.shared import Entity, Repository


class RepositoryNotFoundError(Repository):
    def registry(self, entity: Entity) -> Entity:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    
    def update(self, entity: Entity) -> Entity:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    
    def remove(self, entity: Entity) -> bool:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    
    def find_by_field(self, entity: Entity) -> List[Entity]:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    
    def get_by_id(self, entity: Entity) -> Entity:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    
    def get_all(self, entity: Entity) -> List[Entity]:
        raise Exception(f'No repository was found for {entity.__class__.__name__} entity.')
    

 
repositories = {'default': RepositoryNotFoundError}


def repository_map(cls):
    repositories.update({cls.__base__.__name__: cls})
    return cls

DB_FRAMEWORK = Config.DB_FRAMEWORK

if DB_FRAMEWORK is None:
    raise Exception('There is no a repository framework name defined in enviroment.')


here = Path(os.path.dirname(__file__))
for framework in here.iterdir():
    if framework.is_dir() and framework.name in DB_FRAMEWORK:
        for repository in framework.iterdir():
            if repository.name.endswith('_repository.py') \
                    and not repository.name.startswith('_'):
                framework_name = framework.name
                repository_name = repository.name.split('.')[0]

                module = import_module('src.external.persistence.{}.{}'.format(framework_name, repository_name))
                # print('src.external.persistence.{}.{}'.format(framework_name, repository_name))
