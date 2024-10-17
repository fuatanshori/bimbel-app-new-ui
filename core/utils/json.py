import json
from django.core.serializers.json import DjangoJSONEncoder

class JSONSerializer:
    def dumps(self, value):
        return json.dumps(value, cls=DjangoJSONEncoder)

    def loads(self, value):
        return json.loads(value)