from django.conf.urls import url
from django.contrib import admin

from .views import (
    PagamentoCreateAPIView,
    PagamentoDeleteAPIView,
    PagamentoDetailAPIView,
    PagamentoListAPIView,
    PagamentoUpdateAPIView,
    PagamentoListAllAPIView,
    get_resumo_mes,
    get_pagamento_professor,
    ResumoMensalListAllAPIView


)

urlpatterns = [
    url(r'^$', PagamentoListAPIView.as_view(), name='list'),
    url(r'^list-all/$', PagamentoListAllAPIView.as_view(), name='list-all'),
    url(r'^resumo-mes/$', get_resumo_mes, name='resumo-mes'),
    url(r'^pagamento-professores/$', get_pagamento_professor, name='pagamento-mes'),
    url(r'^historico/$', ResumoMensalListAllAPIView.as_view(), name='historico'),
    url(r'^create/$', PagamentoCreateAPIView.as_view(), name='create'),
    url(r'^add-experimental/$', PagamentoCreateAPIView.as_view(), name='experimental'),
    url(r'^add-avulsa/$', PagamentoCreateAPIView.as_view(), name='avulsa'),
    url(r'^add-personal/$', PagamentoCreateAPIView.as_view(), name='personal'),
    url(r'^(?P<id>[\w-]+)/$',
        PagamentoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        PagamentoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        PagamentoDeleteAPIView.as_view(), name='delete'),

]
