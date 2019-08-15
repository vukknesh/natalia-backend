from django.conf.urls import url
from django.contrib import admin

from .views import (
    EventoCreateAPIView,
    EventoDeleteAPIView,
    EventoDetailAPIView,
    EventoListAPIView,
    EventoUpdateAPIView,

)

urlpatterns = [
    url(r'^$', EventoListAPIView.as_view(), name='list'),
    url(r'^create/$', EventoCreateAPIView.as_view(), name='create'),
    url(r'^(?P<id>[\w-]+)/$', EventoDetailAPIView.as_view(), name='detail'),
    url(r'^(?P<id>[\w-]+)/edit/$',
        EventoUpdateAPIView.as_view(), name='update'),
    url(r'^(?P<id>[\w-]+)/delete/$',
        EventoDeleteAPIView.as_view(), name='delete'),

]
