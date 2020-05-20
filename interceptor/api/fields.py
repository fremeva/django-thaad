import json

from rest_framework.fields import CharField


class JSONTextField(CharField):
    def to_representation(self, value):
        value = super(JSONTextField, self).to_representation(value)
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError:
            return {}
