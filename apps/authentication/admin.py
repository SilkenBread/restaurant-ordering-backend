from django.contrib import admin
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    search_fields = ('id','name','content_type','codename')
    list_display = ('id','name','content_type','codename')
    list_filter = ['content_type__model']

@admin.register(ContentType)
class ContentTypeAdmin(admin.ModelAdmin):
    search_fields = ('id','app_label','model')
    list_display = ('id','app_label','model')
    list_filter = ['app_label','model']
