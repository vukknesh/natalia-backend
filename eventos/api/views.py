from django.db.models import Q

from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView

from rest_framework.filters import (
    SearchFilter,
    OrderingFilter,
)
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
)


from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

)
from django_filters import rest_framework as filters
from eventos.models import Evento


from .permissions import IsOwnerOrReadOnly

from .serializers import (
    EventoCreateUpdateSerializer,
    EventoDetailSerializer,
    EventoListSerializer
)

import django_filters
from django.db.models import Q


class EventoFilter(filters.FilterSet):
    multi_name_fields = django_filters.CharFilter(
        method='filter_by_all_name_fields')

    class Meta:
        model = Evento
        fields = []

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(city__icontains=value) | Q(address__icontains=value) | Q(
                state__icontains=value)
        )


class EventoCreateAPIView(CreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EventoDetailAPIView(RetrieveAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    #lookup_url_kwarg = "abc"


class EventoUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoCreateUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        # email send_email


class EventoDeleteAPIView(DestroyAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrReadOnly]


class EventoListAPIView(ListAPIView):
    serializer_class = EventoListSerializer
    # filter_backends = [SearchFilter, OrderingFilter]
    filterset_class = EventoFilter
    permission_classes = [AllowAny]
    # search_fields = ['title', 'content', 'user__first_name']

    def get_queryset(self, *args, **kwargs):

        queryset_list = Evento.objects.all()  # filter(user=self.request.user)
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            ).distinct()
        return queryset_list
