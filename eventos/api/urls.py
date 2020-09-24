from django.conf.urls import url
from django.contrib import admin

from .views import (
    EventoCreateAPIView,
    EventoDeleteAPIView,
    EventoDetailAPIView,
    EventoListAPIView,
    EventoUpdateAPIView,
    EventoListAllAPIView,
    EventoAdminUpdateAPIView,
    delete_all_aulas,
    EventoByProfAPIView,
    EventoRemarcacaoListAllAPIView,
    EventoDesmarcadosListAllAPIView,
    EventoDesmarcadoByProfAPIView
)

urlpatterns = [
    url(r'^$', EventoListAPIView.as_view(), name='list'),
    url(r'^list-all/$', EventoListAllAPIView.as_view(), name='list-all'),
    url(r'^mostrar-desmarcados/$',
        EventoDesmarcadosListAllAPIView.as_view(), name='desmarcados'),
    url(r'^desmarcado-by-prof/$',
        EventoDesmarcadoByProfAPIView.as_view(), name='desbyprof'),
    url(r'^add-remarcacao/$',
        EventoCreateAPIView.as_view(), name='remarcacao'),
    url(r'^list-by-professor/$',
        EventoByProfAPIView.as_view(), name='prof-aulas'),
    url(r'^create/$', EventoCreateAPIView.as_view(), name='create'),
    url(r'^delete-all/(?P<alunoId>[\w-]+)$',
        delete_all_aulas, name='delete-all'),
    url(r'^(?P<id>[\w-]+)/$', EventoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        EventoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/admin-edit/$',
        EventoAdminUpdateAPIView.as_view(), name='admin-update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        EventoDeleteAPIView.as_view(), name='delete'),

]
