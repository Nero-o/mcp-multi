from datetime import datetime

def converte_datetime_to_isoformat(obj):
    for key, value in obj.items():
        if isinstance(value, datetime):
            obj[key] = value.isoformat()
    return obj