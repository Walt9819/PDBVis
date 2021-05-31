from django.urls import path, re_path
from .views import getModel

urlpatterns = [
    re_path(r'download/(?P<modelID>[0-9A-z]{4,})', getModel, name='getModel'),
]
