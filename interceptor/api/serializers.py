from rest_framework import serializers

from interceptor.api.fields import JSONTextField
from interceptor.models import InterceptedRequest


class InterceptedRequestModelSerializer(serializers.ModelSerializer):
    data = JSONTextField()
    metadata = JSONTextField()
    params = JSONTextField()
    headers = JSONTextField()

    class Meta:
        model = InterceptedRequest
        fields = (
            'id',
            'path',
            'method',
            'params',
            'data',
            'metadata',
            'created_at',
            'headers',
            'content_type',
            'timestamp',
            'session',
        )
