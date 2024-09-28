# health_chat_app/urls.py

from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),
    path('templates/favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
]
