from rest_framework import serializers

from interceptor.api.fields import JSONTextField
from interceptor.models import InterceptedRequest, InterceptorMockResponse
from rest_framework.status import HTTP_200_OK


class InterceptorMockResponseSerializer(serializers.ModelSerializer):
    headers = JSONTextField(source='response_headers')
    data = JSONTextField(source='response_body')

    class Meta:
        model = InterceptorMockResponse
        fields = (
            'status_code',
            'headers',
            'data',
        )


class InterceptedRequestModelSerializer(serializers.ModelSerializer):
    data = JSONTextField()
    metadata = JSONTextField()
    params = JSONTextField()
    headers = JSONTextField()
    response = serializers.SerializerMethodField(source='matched_response')

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
            'response'
        )

    def get_response(self, obj):
        if obj.matched_response:
            data = InterceptorMockResponseSerializer(obj.matched_response).data
            data.update({'match': True})
            return data
        return {
            "match": False,
            "data": {'status': 'You have sent a request, but we encourage you to create your own sessions!'},
            "status_code": HTTP_200_OK,
            "headers": {}
        }
