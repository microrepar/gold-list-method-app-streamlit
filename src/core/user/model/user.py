import datetime
from src.core.shared.entity import Entity


class User(Entity):

    def __init__(self,
                 id_             : int = None,
                 created_at      : datetime.date = None,
                 status          : str = None,
                 name            : str = None,
                 age             : int = None,
                 email           : str = None,
                 profile         : str = None,
                 username        : str = None,
                 password        : str = None,
                 repeat_password : str = None):
        
        self.id              = id_
        self.created_at      = created_at
        self.status          = status
        self.name            = name
        self.age             = age
        self.email           = email
        self.profile         = profile
        self.username        = username
        self.password        = password
        self.repeat_password = repeat_password

    def validate(self):
        return super().validate()

    def __repr__(self) -> str:
        return ('User('
            f'id_={self.id}, '
            f'created_at={self.created_at}, '
            f'status={self.status}, '
            f'name={self.name}, '
            f'age={self.age}, '
            f'email={self.email}, '
            f'profile={self.profile}, '
            f'username={self.username}, '
            f'password={self.password}, '
            f'repeat_password={self.repeat_password}'
            ')'
        )
    
    def to_dict_with_prefix(self):
        return {
            'user_id_': self.id,
            'user_created_at': self.created_at,
            'user_status': self.status,
            'user_name': self.name,
            'user_age': self.age,
            'user_email': self.email,
            'user_profile': self.profile,
            'user_username': self.username,
            'user_password': self.password,
            'user_repeat_password': self.repeat_password,
        }
    
    def data_to_dataframe(self):
        return [
            {
                'id': self.id,
                'username': self.username,
                'created_at': self.created_at,
                'name': self.name,
                'email': self.email,
                'status': self.status,
                'profile': self.profile,
                # 'age': self.age,
                # 'password': self.password,
                # 'repeat_password': self.repeat_password,
            }
        ]