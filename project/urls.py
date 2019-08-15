
from django.contrib import admin
from django.conf.urls import url, include as inc
from django.urls import path, include
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('userprofile.urls')),
    url(r'^api/eventos/', inc(("eventos.api.urls", 'eventos'),
                              namespace='eventos-api')),
]
