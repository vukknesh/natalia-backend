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
from rest_framework.pagination import LimitOffsetPagination
from datetime import datetime, timezone, timedelta, date
from django.contrib.auth.models import User
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

)
from django_filters import rest_framework as filters
from eventos.models import Evento

from rest_framework.decorators import api_view
from .permissions import IsOwnerOrReadOnly

from .serializers import (
    EventoCreateUpdateSerializer,
    EventoDetailSerializer,
    EventoListSerializer,
    EventoListAllSerializer
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


class EventoRemarcacaoListAllAPIView(CreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        print(f'self.request.data  = {self.request.data}')
        Evento.objects.create(
            user=self.request.data['user'], starting_date=self.request.data['starting_date'])


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
        # tudo calculado 3 horas a mais pelo timezone UTC
        user = self.request.user
        now = datetime.now(timezone.utc)
        evento = self.get_object()
        # print now.year, now.month, now.day, now.hour, now.minute, now.second
        year = now.year
        month = now.month
        diff = evento.starting_date - now
        # duration_in_s = diff.total_seconds()
        # print(f'duration in s = {duration_in_s}')
        days, seconds = diff.days, diff.seconds
        dif_hours = days * 24 + seconds
        print(f'dif_hours = {dif_hours}')
        response_text = 'Aula desmarcada com sucesso!'
        bonus_counter = user.profile.bonus_remarcadas
        aulas_counter = user.profile.aulas_remarcadas
        if(evento.desmarcado):
            raise ValidationError({"message": "Aula já desmarcada!"})
        # if(evento.bonus):
        #    raise ValidationError(
        #        {"message": "Esta é uma aula bônus e não poderá ser remarcada!"})
        if(evento.starting_date.hour <= 12):
            # evento proximo dia
            if(now.hour >= 23 and ((evento.starting_date.day - now.day) == 1)):
                print(f'um dia anterior')
                raise ValidationError(
                    {"message": "Você só poderá remarcar aulas matutinas antes das 20hrs do dia anterior."})
            # msm dia que evento matutino
            if(now.date() == evento.starting_date.date()):
                print(f'same date')
                raise ValidationError(
                    {"message": "Você só poderá remarcar aulas matutinas antes das 20hrs do dia anterior."})
            pass
        # funcionando

        if(dif_hours <= 0):
            print('dentro')
            raise ValidationError(
                {"message": "Você só poderá remarcar aulas 3 horas antes."})
        dia_pg = user.profile.dia_pagamento
        month_mais = month + 1
        start_date = f'{year}-{month}-{dia_pg} 00:00:00'

        if month_mais == 13:
            month_mais = 1
            year = year + 1

        end_date = f'{year}-{month_mais}-{dia_pg} 00:00:00'
        aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                              starting_date__lt=end_date)
        # aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
        #                                       starting_date__month__gte=month,
        #                                       starting_date__year__lte=year,
        #                                       starting_date__month__lte=month)
        # aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
        #                                      starting_date__month__gte=month,
        #                                      starting_date__year__lte=year,
        #                                      starting_date__month__lte=month)

        if(user.profile.plano == "4 Aulas"):

            if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas > 0):
                aulas_counter = aulas_counter + 1
                pass
            if(user.profile.aulas_remarcadas > 0):
                raise ValidationError(
                    {"message": "Você já remarcou 1 aula deste mês."})

        if(user.profile.plano == "8 Aulas"):
            aulas_bonus = aulas_do_mes.count() - 8
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            # if(aulas_do_mes.count() > 8 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
                aulas_counter = aulas_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas > 1):
                aulas_counter = aulas_counter + 1
                pass
            if(user.profile.aulas_remarcadas > 1):
                raise ValidationError(
                    {"message": "Você já remarcou 2 aulas deste mês."})

            # if(user.profile.aulas_remarcadas > 1):
            #    raise ValidationError(
            #        {"message": "Você já remarcou 2 aulas deste mês."})
            # if(aulas_do_mes.count() > 8):
            #    if(aulas_do_mes.last() == evento):
            #        raise ValidationError(
            #            {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
            #    pass

        if(user.profile.plano == "12 Aulas"):
            aulas_bonus = aulas_do_mes.count() - 12
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 3 and user.profile.bonus_remarcadas <= 3):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            # if(aulas_do_mes.count() > 8 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
                aulas_counter = aulas_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas == 2):
                aulas_counter = aulas_counter + 1
                pass
            if(aulas_bonus == 3 and user.profile.bonus_remarcadas == 3):
                aulas_counter = aulas_counter + 1
                pass
            # if(aulas_do_mes.count() > 12 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            # if(aulas_do_mes.count() > 12 and user.profile.bonus_remarcadas > 0):
            #    aulas_counter = aulas_counter + 1
            #    pass
            if(user.profile.aulas_remarcadas > 2):
                raise ValidationError(
                    {"message": "Você já remarcou 3 aulas deste mês."})

        profile = user.profile
        profile.aulas_remarcadas = aulas_counter
        profile.bonus_remarcadas = bonus_counter
        profile.save()
        print(f'finalizou com perfil salvo + 1 {profile.aulas_remarcadas}')

        serializer.save(user=user)

        # email send_email


class EventoDeleteAPIView(DestroyAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoDetailSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]


class EventoListAPIView(ListAPIView):
    serializer_class = EventoListSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # this makes post method on listapiview
        return self.list(request, *args, **kwargs)

    def list(self, request):
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month
        dt = date.today()

        if request.data['user_id'] is not None:
            u = User.objects.get(id=request.data['user_id'])
        else:
            u = User.objects.first()

        dia_pg = u.profile.dia_pagamento
        month_mais = month + 1

        start_date = f'{year}-{month}-{dia_pg} 00:00:00'
        if month_mais == 13:
            month_mais = 1
            year = year + 1

        end_date = f'{year}-{month_mais}-{dia_pg} 00:00:00'
        print(f'start_date  {start_date}')
        print(f'end_date  {end_date}')
        # qs = Evento.objects.filter(starting_date__gte=datetime.now(), starting_date__year__gte=year,
        #                           starting_date__month__gte=month, starting_date__year__lte=year, starting_date__month__lte=month)
        queryset_list = Evento.objects.filter(
            user=u).filter(starting_date__gte=dt, starting_date__year__gte=year,
                           starting_date__month__gte=month, starting_date__day__gte=dia_pg, starting_date__year__lte=year, starting_date__month__lte=month_mais, starting_date__day__lt=dia_pg)
        print(f'queryset_list === {queryset_list}')
        qs = Evento.objects.filter(user=u).filter(starting_date__gte=dt,
                                                  starting_date__lt=end_date)
        for qqq in qs:
            print(f'qqq.starting_date.day = {qqq.starting_date.day}')
        print(f'qs === {qs}')
        # queryset_list = Evento.objects.filter(
        #    user=u).filter(starting_date__gte=datetime.now(), starting_date__year__gte=year,
        #                   starting_date__month__gte=month, starting_date__year__lte=year, starting_date__month__lte=month)
        # .filter(starting_date__gte=datetime.now())  # filter(user=self.request.user)

        return Response({"eventos": EventoListSerializer(qs, many=True).data})


class EventoListAllAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        dt = date.today() - timedelta(5)

        queryset_list = Evento.objects.filter(user__is_active=True).filter(starting_date__gte=dt)[
            :900]  # filter(user=self.request.user)
        print(f'querylist = {queryset_list}')

        return queryset_list


class EventoDesmarcadosListAllAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        dt = date.today() - timedelta(30)
        queryset_list = Evento.objects.filter(
            starting_date__gte=dt, desmarcado=True)
        print(f'desmarcados = {queryset_list}')

        return queryset_list


class EventoByProfAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    page_size = 200

    def get_queryset(self, *args, **kwargs):
        dt = date.today() + timedelta(30)
        queryset_list = Evento.objects.filter(
            user__profile__professor=self.request.user).filter(user__is_active=True, starting_date__gte=date.today(), starting_date__lte=dt)  # filter(user=self.request.user)
        print(f'querylist = {queryset_list}')

        return queryset_list


class EventoDesmarcadoByProfAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination
    page_size = 200

    def get_queryset(self, *args, **kwargs):
        print('dentro do query')
        print(f'self.request.user = {self.request.user}')
        queryset_list = Evento.objects.filter(
            user__profile__professor=self.request.user).filter(user__is_active=True).filter(desmarcado=True)  # filter(user=self.request.user)
        print(f'querylist = {queryset_list}')

        return queryset_list


class EventoAdminUpdateAPIView(UpdateAPIView):
    queryset = Evento.objects.filter(starting_date__gte=datetime.now())
    serializer_class = EventoCreateUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsAdminUser]

    def perform_update(self, serializer):
        user = self.request.user

        evento = self.get_object()
        serializer.save(user=user)


@api_view(['GET'])
def delete_all_aulas(request, alunoId):
    user = User.objects.get(id=alunoId)

    Evento.objects.filter(user=user).delete()

    return Response({"message": "Todas Aulas Deletadas"})
