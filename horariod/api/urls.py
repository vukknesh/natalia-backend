from django.conf.urls import url
from django.contrib import admin

from .views import (
    HorarioCreateAPIView,
    HorarioDetailAPIView,
    add_reposicao,
    repor_aula,
    get_horarios_disponiveis
)

urlpatterns = [

    url(r'^add-reposicao/$',
        add_reposicao, name='add-reposicao'),
    url(r'^create/$', HorarioCreateAPIView.as_view(), name='create'),
    url(r'^repor-aula/$',
        repor_aula, name='repor-aula'),
    url(r'^disponiveis/$',
        get_horarios_disponiveis, name='disponiveis'),

    url(r'^(?P<id>[\w-]+)/$', HorarioDetailAPIView.as_view(), name='detail'),


]
