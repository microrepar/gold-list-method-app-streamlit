"""[summary]
"""
import abc
from collections import OrderedDict
import datetime
from enum import Enum
import inspect
from typing import Any, Dict, List

from src.core.shared.application import Result
from src.core.shared.entity import Entity

primitive_types = [int, float, str, bool, bytes, datetime.date, dict, set] + Enum.__subclasses__()
ENTITY_MAP = {s.__name__: s for s in Entity.__subclasses__()}

class AbstractViewHelper(abc.ABC):
    @abc.abstractmethod
    def get_entities(self, *args: List[Entity], request: dict):
        """Receives a request and returns an instance of the object with the data filled in
        """

    @abc.abstractmethod
    def set_view(self, result: Result, request: dict):
        """Receives the request result object and prepares it to present in the view to the client
        """


#########################Implementation############################

class GenericViewHelper(AbstractViewHelper):

    def get_entities(self, *args: List[Entity], request: dict):        

        domain_entities: List[Entity] = []

        # Iterates the list of classes to fill them with the request data
        for cls in args:

            # Retrieves the name of the class to use in retrieving request data
            class_name = cls.__name__.lower()

            entity_signature = inspect.signature(cls)

            kwargs = OrderedDict()
            for name, param in entity_signature.parameters.items():

                param_annotation = param.annotation
                if isinstance(param.annotation, str):
                    param_annotation = ENTITY_MAP.get(param.annotation, param.annotation)
                
                param_value = request.get(f'{class_name}_{name}')
                if param_value is None: continue
                
                if param_annotation in primitive_types:
                    if param_annotation in (datetime.date, ):
                        # TODO: create a function to prepare date value 
                        if param_annotation == type(param_value):
                            kwargs[name] = param_value
                    else:
                        kwargs[name] = param_annotation(param_value)
                
                elif getattr(param_annotation, '__base__', None) == Entity:
                    inner_class_param = [param_annotation]
                    inner_value: List[Dict[str: Any]] = request.get(f'{class_name}_{name}')                    
                    kwargs[name] : List[Entity] = self.get_entities(*inner_class_param, request=inner_value)[-1] # type: ignore

                elif hasattr(param_annotation, '__origin__') \
                        and param_annotation.__origin__ is list:                    
                    if len(param_annotation.__args__) == 1 \
                            and getattr(param.annotation.__args__[0], '__base__', None) == Entity:                        
                        inner_cls = param.annotation.__args__[0]
                        inner_class_param = [inner_cls]                        
                        values: List[Dict[str: Any]] = request.get(f'{class_name}_{name}')
                        if values:
                            attr_list = []
                            for inner_value in values:
                                attr_list.append(
                                    self.get_entities(*inner_class_param, request=inner_value)[-1]
                                )                
                            kwargs[name] = attr_list

                    else:
                        kwargs[name] = param_value
             
            entity = cls(**kwargs)

            domain_entities.append(entity)

        return domain_entities
    

    def set_view(self, result: Result, request):
        return result.to_dict()