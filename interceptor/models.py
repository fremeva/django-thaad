import string
import random

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from interceptor.choices import HTTP_REQUEST_METHODS
from interceptor import validators


def session_upload_to(instance, filename):

    if instance.request.session is None:
        return f'{instance.request.id}/files/{filename}'

    session = instance.request.session
    return f'{session.user.username}/{session.short_name}/files/{filename}'


class InterceptedRequest(models.Model):
    path = models.CharField(max_length=255, default='/')
    method = models.CharField(max_length=20)
    params = models.TextField(null=True, blank=True)
    data = models.TextField(null=True, blank=True)
    metadata = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    headers = models.TextField(null=True, blank=True)
    content_type = models.CharField(max_length=30, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    session = models.ForeignKey('InterceptorSession', null=True, blank=True, on_delete=models.CASCADE,
                                related_name='requests')
    matched_response = models.ForeignKey('InterceptorMockResponse', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'[{self.method}] {self.created_at}'


class InterceptedFile(models.Model):
    request = models.ForeignKey(InterceptedRequest, on_delete=models.CASCADE, related_name='files')
    parameter = models.CharField(max_length=250)
    filename = models.CharField(max_length=250)
    size = models.FloatField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, upload_to=session_upload_to)

    def __str__(self):
        return self.filename


class InterceptorSession(models.Model):
    short_name = models.CharField(max_length=20, blank=True)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=True)
    requires_authentication = models.BooleanField(default=False)
    saves_files = models.BooleanField(default=False)
    session_token = models.CharField(max_length=24, null=True, blank=True)
    creation_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('short_name', 'user')

    def __str__(self):
        return self.short_name

    def clean(self):
        if self.short_name.lower() in ['interceptor', 'console']:
            raise ValidationError(
                f'Word "{self.short_name.capitalize()}" is a reserved word as session. Please select another name'
            )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if not self.short_name:
            exists = True
            while exists:
                short_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=5))
                exists = InterceptorSession.objects.filter(short_name=short_name, user=self.user).exists()

            self.short_name = short_name
        super(InterceptorSession, self).save(force_insert, force_update, using, update_fields)

    def generate_new_token(self):
        equal = True
        new_token = ''

        while equal:
            new_token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=24))
            equal = new_token == self.session_token

        self.session_token = new_token
        self.save()


class InterceptorMockResponse(models.Model):
    session = models.ForeignKey(InterceptorSession, on_delete=models.CASCADE, related_name='mocks')

    # Request descriptor
    method = models.CharField(max_length=8, choices=HTTP_REQUEST_METHODS, default='get')
    path = models.CharField(max_length=255, default='/')

    # Response template
    status_code = models.PositiveIntegerField()
    response_headers = models.TextField(null=True, blank=True,
                                        validators=[validators.JSONFormatValidator(allow_null=True)])
    response_body = models.TextField(validators=[validators.JSONFormatValidator()])

    # Aditionals
    response_description = models.TextField(max_length=255)

    def __str__(self):
        return f'{self.get_method_display()} {self.path} => {self.status_code}'
