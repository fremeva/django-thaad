from django.conf import settings
from django.contrib import admin

from interceptor.models import InterceptedRequest, InterceptedFile, InterceptorSession, InterceptorMockResponse


class InterceptedFileTabularInline(admin.TabularInline):
    model = InterceptedFile
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj):
        return False


class InterceptedRequestModelAdmin(admin.ModelAdmin):
    inlines = [InterceptedFileTabularInline, ]


admin.site.register(InterceptedRequest, InterceptedRequestModelAdmin)


class InterceptorMockResponseTabularInline(admin.TabularInline):
    model = InterceptorMockResponse


class InterceptorSessionModelAdmin(admin.ModelAdmin):

    list_display = ('short_name', 'active')

    inlines = [InterceptorMockResponseTabularInline]

    actions = ('generate_new_token', )

    def get_list_display(self, request):
        if request.user.is_superuser:
            return ('id', ) + self.list_display + ('user', )
        return self.list_display

    def get_fields(self, request, obj=None):
        fields = ['short_name', 'active', 'requires_authentication', 'saves_files', 'session_token']

        if settings.DEBUG:
            fields.append('user')

        return fields

    def get_readonly_fields(self, request, obj=None):
        return ('session_token', )

    def save_model(self, request, obj, form, change):
        if not settings.DEBUG or obj.user is None:
            obj.user = request.user
        obj.save()

    def get_queryset(self, request):
        qs = super(InterceptorSessionModelAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)

    def generate_new_token(self, request, queryset):
        for session in queryset:
            session.generate_new_token()

    generate_new_token.short_description = 'Generate new session token'


admin.site.register(InterceptorSession, InterceptorSessionModelAdmin)

