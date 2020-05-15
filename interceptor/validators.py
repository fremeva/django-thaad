import json

from django.core.exceptions import ValidationError


class JSONFormatValidator:
    def __init__(self, allow_null=False):
        self.allow_null = allow_null

    def __call__(self, value):
        if not value and self.allow_null:
            return
        try:
            json.loads(value)
        except json.decoder.JSONDecodeError:
            raise ValidationError('Value is not a valid JSON string.')
