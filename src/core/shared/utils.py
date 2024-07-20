import datetime
from dateutil import parser


def date_to_string(date_obj: datetime.date, format='%Y-%m-%d') -> str:
    if date_obj is not None:
        return date_obj.strftime(format)


def datetime_to_string(datetime_obj: datetime.datetime, format='%d/%m/%Y %H:%M:%S') -> str:
    if datetime_obj is not None:
        return datetime_obj.strftime(format)
    

def string_to_date(string: str) -> datetime.date:    
    formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%d/%m/%Y', '%Y-%m-%d']
    for format in formats:
        try:
            datetime_obj = datetime.datetime.strptime(string, format)
            return datetime_obj.date()
        except Exception: ...

    

def string_to_datetime(string: str) -> datetime.date:
    formats = ['%Y-%m-%dT%H:%M:%S.%fZ', '%d/%m/%Y', '%Y-%m-%d']
    for formato in formats:
        try:
            datetime_obj = datetime.datetime.strptime(string, format)
            return datetime_obj
        except Exception: ...
