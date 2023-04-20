from decimal import Decimal

import json


class CustomEncoder(json.JSONEncoder):
    """Encodes Object to json
    Args:
        json (_type_): _description_
    """

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, set):
            return list(obj)
        return json.JSONEncoder.default(self, obj)