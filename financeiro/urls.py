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
    ResumoMensalListAllAPIView,
    AulaExperimentalCreateAPIView,
    AulaAvulsaGrupoCreateAPIView,
    AulaPersonalCreateAPIView,
    VendaItemsCreateAPIView,
    ItemCreateAPIView,
    ItemsListAllAPIView,
    PagamentoPorAulunoAPIView,
    TesteListAllAPIView,
    pagamentos_pendentes,
    mercadopago_pix,
    ResumoManualMesListAllAPIView,
    mensal_por_professor

)

urlpatterns = [
    url(r'^$', PagamentoListAPIView.as_view(), name='list'),
    url(r'^list-all/$', PagamentoListAllAPIView.as_view(), name='list-all'),
    url(r'^teste/$', TesteListAllAPIView.as_view(), name='teste'),
    url(r'^res-mes/$', ResumoManualMesListAllAPIView.as_view(), name='teste'),
    url(r'^por-aluno/$', PagamentoPorAulunoAPIView.as_view(), name='por-aluno'),
    url(r'^list-items/$', ItemsListAllAPIView.as_view(), name='list-items'),
    url(r'^resumo-mes/$', get_resumo_mes, name='resumo-mes'),
    url(r'^pendentes/$', pagamentos_pendentes, name='pendentes'),
    url(r'^pag-professor/$', mensal_por_professor, name='pendentes'),
    url(r'^mercadopago-pix/$', mercadopago_pix, name='mercadopago-pix'),
    url(r'^pagamento-professores/$', get_pagamento_professor, name='pagamento-mes'),
    url(r'^historico/$', ResumoMensalListAllAPIView.as_view(), name='historico'),
    url(r'^create/$', PagamentoCreateAPIView.as_view(), name='create'),
    url(r'^add-item/$',
        ItemCreateAPIView.as_view(), name='item'),
    url(r'^add-vendaitems/$',
        VendaItemsCreateAPIView.as_view(), name='venda-items'),
    url(r'^add-experimental/$',
        AulaExperimentalCreateAPIView.as_view(), name='experimental'),
    url(r'^add-avulsa/$', AulaAvulsaGrupoCreateAPIView.as_view(), name='avulsa'),
    url(r'^add-personal/$', AulaPersonalCreateAPIView.as_view(), name='personal'),

    url(r'^(?P<id>[\w-]+)/$',
        PagamentoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        PagamentoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        PagamentoDeleteAPIView.as_view(), name='delete'),

]
