from django.db.models import Q

from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
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
from datetime import datetime, timezone

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
    queryset = Evento.objects.filter(starting_date__gte=datetime.now())
    serializer_class = EventoDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    # lookup_url_kwarg = "abc"


class EventoUpdateAPIView(UpdateAPIView):
    queryset = Evento.objects.filter(starting_date__gte=datetime.now())
    serializer_class = EventoCreateUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        user = self.request.user
        now = datetime.now(timezone.utc)
        evento = self.get_object()
        # print now.year, now.month, now.day, now.hour, now.minute, now.second
        year = now.year
        month = now.month
        print(f'evento = {evento}')
        print(f'evento.time.hour = {evento.time.hour}')
        print(f'user.first_name = {user.first_name}')

        print(f'evento.time.hour = {evento.time.hour}')
        if(evento.time.hour <= 12):
            # evento proximo dia
            if(now.hour > 20 and ((now.day - evento.starting_date.day).days == -1)):
                raise ValidationError(
                    {"message": "Voce so pode remarcar aulas matutinas antes das 20hrs do dia anterior."})
            # msm dia que evento matutino
            if(((now.day - evento.starting_date.day).days == 0)):
                raise ValidationError(
                    {"message": "Voce so pode remarcar aulas matutinas antes das 20hrs do dia anterior."})
            pass
        # funcionando
        if(evento.time.hour > 12 and evento.time.hour <= 24 and (evento.starting_date.hour - now.hour < 3)):
            raise ValidationError(
                {"message": "Voce so pode remarcar aulas 3 horas antes."})
        aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
                                              starting_date__month__gte=month,
                                              starting_date__year__lte=year,
                                              starting_date__month__lte=month)
        print(f'aulas_do_mes = {aulas_do_mes}')
        print(f'user.profile.plano = {user.profile.plano}')
        if(user.profile.plano == "4 Aulas"):
            if(user.profile.aulas_remarcadas > 0):
                raise ValidationError(
                    {"message": "Voce ja remarcou 1 aula deste mes."})
            if(aulas_do_mes.count() > 4):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass
        if(user.profile.plano == "8 Aulas"):
            if(user.profile.aulas_remarcadas > 1):
                raise ValidationError(
                    {"message": "Voce ja remarcou 2 aulas deste mes."})
            if(aulas_do_mes.count() > 8):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass

        if(user.profile.plano == "12 Aulas"):
            if(user.profile.aulas_remarcadas > 2):
                raise ValidationError(
                    {"message": "Voce ja remarcou 3 aulas deste mes."})
            if(aulas_do_mes.count() > 12):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass
        profile = user.profile
        profile.aulas_remarcadas = profile.aulas_remarcadas + 1
        profile.save()
        serializer.save(user=user)
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
        queryset_list = Evento.objects.filter(
            starting_date__gte=datetime.now())  # filter(user=self.request.user)
        print(queryset_list)
        query = self.request.GET.get("q")
        if query:
            queryset_list = queryset_list.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query)
            ).distinct()
        return queryset_list
