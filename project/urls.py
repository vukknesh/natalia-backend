
from django.contrib import admin
from django.conf.urls import url, include as inc
from django.urls import path, include
urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('', include('userprofile.urls')),
    url(r'^api/eventos/', inc(("eventos.api.urls", 'eventos'),
                              namespace='eventos-api')),
    url(r'^api/horario/', inc(("horariod.api.urls", 'horariod'),
                              namespace='horariod-api')),
    url(r'^api/financeiro/', inc(("financeiro.urls", 'financeiro'),
                                 namespace='financeiro-api')),
]
