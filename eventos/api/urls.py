from django.conf.urls import url
from django.contrib import admin

from .views import (
    EventoCreateAPIView,
    EventoDeleteAPIView,
    EventoDetailAPIView,
    EventoListAPIView,
    EventoUpdateAPIView,
    EventoListAllAPIView,
    EventoAdminUpdateAPIView

)

urlpatterns = [
    url(r'^$', EventoListAPIView.as_view(), name='list'),
    url(r'^list-all/$', EventoListAllAPIView.as_view(), name='list-all'),
    url(r'^create/$', EventoCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>[\w-]+)/$', EventoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        EventoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/admin-edit/$',
        EventoAdminUpdateAPIView.as_view(), name='admin-update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        EventoDeleteAPIView.as_view(), name='delete'),

]
