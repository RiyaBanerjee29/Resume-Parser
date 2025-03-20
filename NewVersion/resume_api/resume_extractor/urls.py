from django.urls import path
from .views import upload_resume

urlpatterns = [
       path('extract/', upload_resume, name='extract-resume'),
]
