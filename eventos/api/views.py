from django.db.models import Q
from itertools import chain
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from calendar import monthrange
from userprofile.models import Profile
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
from dateutil.relativedelta import relativedelta
from django.contrib.auth.models import User
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

)
from django_filters import rest_framework as filters
from financeiro.models import Experimental
from financeiro.serializers import ExperimentalSerializer
from eventos.models import Evento
from calendar import monthrange
from rest_framework.decorators import api_view, permission_classes
from .permissions import IsOwnerOrReadOnly

from .serializers import (
    EventoCreateUpdateSerializer,
    EventoDetailSerializer,
    EventoListSerializer,
    EventoListAllSerializer
)

import django_filters


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
        print('dentro do create')
        print('self', self)

        data = datetime.now()
        if self.request.data['starting_date']:
            data = self.request.data['starting_date']
        if self.request.data['user']:

            user = User.objects.get(id=self.request.data['user'])
        else:
            user = self.request.user

        if Evento.objects.exclude(pk=self.pk).filter(starting_date=self.starting_date).exists():
            print('existe dentro do perform create ')
            raise ValueError

        serializer.save(user=user, starting_date=data)


class EventoRemarcacaoListAllAPIView(CreateAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoCreateUpdateSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):

        if self.request.data['user'] is not None:
            u = User.objects.get(id=self.request.data['user'])
        else:
            u = User.objects.first()
        print(f'user = {u}')
        serializer.save(user=u)


@api_view(['POST'])
def add_reposicao(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    starting_date = request.data['starting_date']
    print(f'starting_date ={starting_date}')

    Evento.objects.create(user=user, starting_date=starting_date, remarcacao=False, reposicao=True,
                          desmarcado=False, bonus=True)

    return Response({"message": "Aula remarcada com sucesso!"})


@api_view(['POST'])
def add_avulsa(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    starting_date = request.data['starting_date']
    print(f'starting_date ={starting_date}')

    Evento.objects.create(user=user, starting_date=starting_date, avulsa=True)

    return Response({"message": "Aula remarcada com sucesso!"})


@api_view(['POST'])
def add_atestado(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    starting_date = request.data['starting_date']
    print(f'starting_date ={starting_date}')

    Evento.objects.create(
        user=user, starting_date=starting_date, atestado=True)

    return Response({"message": "Aula remarcada com sucesso!"})


@api_view(['POST'])
def add_experimental(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    starting_date = request.data['starting_date']
    print(f'starting_date ={starting_date}')

    Evento.objects.create(
        user=user, starting_date=starting_date, experimental=True)

    return Response({"message": "Aula remarcada com sucesso!"})


class EventoDetailAPIView(RetrieveAPIView):
    queryset = Evento.objects.filter(starting_date__gte=datetime.now())
    serializer_class = EventoDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    # lookup_url_kwarg = "abc"


@api_view(['GET'])
def desmarcar_aula_request(request, eventoId):
    user = request.user
    print(f'request= {request}')
    print(f'request.user= {request.user}')
    now = datetime.now(timezone.utc)
    evento = Evento.objects.get(id=eventoId)
    # print now.year, now.month, now.day, now.hour, now.minute, now.second
    year = now.year
    month = now.month
    diff = evento.starting_date - now
    # duration_in_s = diff.total_seconds()
    # print(f'duration in s = {duration_in_s}')
    days, seconds = diff.days, diff.seconds
    dif_hours = days * 24 + seconds
    print(f'diff.seconds = {diff.seconds}')
    print(f'diff.days = {diff.days}')
    print(f'dif_hours = {dif_hours}')
    print(f'agora hora = {now}')
    print(f'evento hora = {evento.starting_date}')
    print(f'agora hora = {now}')

    response_text = "Ok"
    dt = date.today()
    bonus_counter = user.profile.bonus_remarcadas
    aulas_counter = user.profile.aulas_remarcadas

    if(evento.reposicao):
        response_text = 'Você esta desmarcando uma aula de reposição e não poderá reagendá-la.'
        return Response({"message": response_text, "aulas_remarcadas": aulas_counter, "bonus_remarcadas": bonus_counter})

    if(evento.desmarcado):
        raise ValidationError({"message": "Aula já desmarcada!"})

    if(evento.starting_date.hour <= 12):
        # evento proximo dia
        if(now.hour >= 23 and ((evento.starting_date.day - now.day) == 1)):
            print(f'um dia anterior')

            response_text = "Você só poderá remarcar aulas matutinas antes das 20hrs do dia anterior."

        # msm dia que evento matutino
        if(now.date() == evento.starting_date.date()):
            print(f'same date')

            response_text = "Você só poderá remarcar aulas matutinas antes das 20hrs do dia anterior."
        pass
    # funcionando

    if(dif_hours <= 10800):
        print('dentro')

        response_text = "Você só poderá remarcar aulas 3 horas antes."

    dia_pg = user.profile.dia_pagamento

    a_month = relativedelta(months=1)
    d_day = date(year, month, dia_pg)
    if dt.day < dia_pg:
        start_date = d_day - a_month
        end_date = d_day
    else:
        start_date = d_day
        end_date = d_day + a_month

    aulas_do_mes = user.evento_set.filter(starting_date__range=(
        start_date, end_date), reposicao=False,  historico=False)

    if(user.profile.plano == "4 Aulas"):

        if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas == 0):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas > 0):
            aulas_counter = aulas_counter + 1
            pass
        if(user.profile.aulas_remarcadas > 0):
            response_text = "Você já remarcou 1 aula deste mês e não poderá remarcar outra."

    if(user.profile.plano == "8 Aulas"):
        aulas_bonus = aulas_do_mes.count() - 8
        if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass

        if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas > 1):
            aulas_counter = aulas_counter + 1
            pass
        if(user.profile.aulas_remarcadas > 1):
            response_text = "Você já remarcou 2 aulas deste mês e não poderá remarcar outra."

    if(user.profile.plano == "12 Aulas"):
        aulas_bonus = aulas_do_mes.count() - 12
        if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 3 and user.profile.bonus_remarcadas <= 3):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass

        if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas == 2):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 3 and user.profile.bonus_remarcadas == 3):
            aulas_counter = aulas_counter + 1
            pass

        if(user.profile.aulas_remarcadas > 2):

            response_text = "Você já remarcou 3 aulas deste mês e não poderá remarcar outra."

        # teste ultima aula do mes
        if now.date() == end_date.date():
            response_text = 'Esta aula é a última do seu mês e não poderá ser remarcada!'
    if(user.profile.plano == "16 Aulas"):
        aulas_bonus = aulas_do_mes.count() - 16
        if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 3 and user.profile.bonus_remarcadas <= 3):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 4 and user.profile.bonus_remarcadas <= 4):
            response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass

        if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas == 2):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 3 and user.profile.bonus_remarcadas == 3):
            aulas_counter = aulas_counter + 1
            pass
        if(aulas_bonus == 4 and user.profile.bonus_remarcadas == 4):
            aulas_counter = aulas_counter + 1
            pass

        if(user.profile.aulas_remarcadas > 3):

            response_text = "Você já remarcou 4 aulas deste mês e não poderá remarcar outra."

        # teste ultima aula do mes
        if now.date() == end_date.date():
            response_text = 'Esta aula é a última do seu mês e não poderá ser remarcada!'

    return Response({"message": response_text, "aulas_remarcadas": aulas_counter, "bonus_remarcadas": bonus_counter})


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
        year = now.year
        dt = date.today()
        month = now.month
        diff = evento.starting_date - now
        print(f'diff = {diff}')
        # duration_in_s = diff.total_seconds()
        # print(f'duration in s = {duration_in_s}')
        days, seconds = diff.days, diff.seconds
        dif_hours = days * 24 + seconds
        response_text = "Ok"
        bonus_counter = user.profile.bonus_remarcadas
        aulas_counter = user.profile.aulas_remarcadas

        if(evento.desmarcado):
            raise ValidationError({"message": "Aula já desmarcada!"})
        # if(evento.bonus):
        #    raise ValidationError(
        #        {"message": "Esta é bônus e não poderá ser remarcada!"})

        # funcionando

        dia_pg = user.profile.dia_pagamento
        a_month = relativedelta(months=1)
        d_day = date(year, month, dia_pg)
        if dt.day < dia_pg:
            start_date = d_day - a_month
            end_date = d_day
        else:
            start_date = d_day
            end_date = d_day + a_month
            print(f'start_date > = {start_date}')
            print(f'end_date > = {end_date}')
        aulas_do_mes = user.evento_set.filter(starting_date__range=(
            start_date, end_date), reposicao=False,  historico=False)
        print(f'aulas_do_mes couunt {aulas_do_mes.count()}')

        if(user.profile.plano == "4 Aulas"):
            aulas_bonus = aulas_do_mes.count() - 4
            if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas > 0):
                aulas_counter = aulas_counter + 1
                pass
            if(user.profile.aulas_remarcadas > 0):
                response_text = "Você já remarcou 1 aula deste mês."

        if(user.profile.plano == "8 Aulas"):

            aulas_bonus = aulas_do_mes.count() - 8
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            # if(aulas_do_mes.count() > 8 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas > 0):
                aulas_counter = aulas_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas > 1):
                aulas_counter = aulas_counter + 1
                pass
            if(user.profile.aulas_remarcadas > 1):
                response_text = "Você já remarcou 2 aulas deste mês."

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
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 3 and user.profile.bonus_remarcadas <= 3):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            # if(aulas_do_mes.count() > 8 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é bônus e não poderá ser remarcada!'
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
            #    response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            # if(aulas_do_mes.count() > 12 and user.profile.bonus_remarcadas > 0):
            #    aulas_counter = aulas_counter + 1
            #    pass
            if(user.profile.aulas_remarcadas > 2):

                response_text = "Você já remarcou 3 aulas deste mês."

            if(dif_hours <= 0):
                print('dentro')

                response_text = "Você só poderá remarcar aulas 3 horas antes."
        if(user.profile.plano == "16 Aulas"):
            aulas_bonus = aulas_do_mes.count() - 16
            if(aulas_bonus == 1 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 3 and user.profile.bonus_remarcadas <= 3):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            if(aulas_bonus == 4 and user.profile.bonus_remarcadas <= 4):
                response_text = 'Esta aula é bônus e não poderá ser remarcada!'
                bonus_counter = bonus_counter + 1
                pass
            # if(aulas_do_mes.count() > 8 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é bônus e não poderá ser remarcada!'
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
            if(aulas_bonus == 4 and user.profile.bonus_remarcadas == 4):
                aulas_counter = aulas_counter + 1
                pass
            # if(aulas_do_mes.count() > 12 and user.profile.bonus_remarcadas == 0):
            #    response_text = 'Esta aula é bônus e não poderá ser remarcada!'
            #    bonus_counter = bonus_counter + 1
            #    pass
            # if(aulas_do_mes.count() > 12 and user.profile.bonus_remarcadas > 0):
            #    aulas_counter = aulas_counter + 1
            #    pass
            if(user.profile.aulas_remarcadas > 3):

                response_text = "Você já remarcou 4 aulas deste mês."

        # deixar em cima do profile.bonus_remarcadas se nao conta errado!
        # if aulas_bonus > user.profile.bonus_remarcadas:
        #     print(f'aulas_bonus > = {aulas_bonus}')
        #     remarcacao_aluno = False
        # else:
        #     print(f'aulas_bonus < = {aulas_bonus}')

        #     remarcacao_aluno = True
        remarcacao_aluno = False
        # if aulas_bonus == user.profile.bonus_remarcadas:
        #     remarcacao_aluno = True
        # else:
        #     remarcacao_aluno = False

        if(user.profile.plano == "4 Aulas"):
            if aulas_bonus == 1 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 3:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 0 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 2:
                remarcacao_aluno = True
                pass

        if(user.profile.plano == "8 Aulas"):
            if aulas_bonus == 1 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 4:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 2 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 5:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 0 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 3:
                remarcacao_aluno = True
                pass
        if(user.profile.plano == "12 Aulas"):
            if aulas_bonus == 1 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 5:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 2 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 6:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 3 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 7:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 0 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 4:
                remarcacao_aluno = True
        if(user.profile.plano == "16 Aulas"):
            if aulas_bonus == 1 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 5:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 2 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 6:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 3 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 7:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 4 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 8:
                remarcacao_aluno = True
                pass
            if aulas_bonus == 0 and aulas_bonus == user.profile.bonus_remarcadas and user.profile.aulas_remarcadas < 5:
                remarcacao_aluno = True
        if(dif_hours <= 10800):
            remarcacao_aluno = False

        if(evento.starting_date.hour <= 12):
            print(f'proximo dia')
            # evento proximo dia
            if(now.hour >= 23 and ((evento.starting_date.day - now.day) == 1)):
                remarcacao_aluno = False

            # msm dia que evento matutino
            if(now.date() == evento.starting_date.date()):
                remarcacao_aluno = False

            pass

        profile = user.profile
        profile.aulas_remarcadas = aulas_counter
        profile.bonus_remarcadas = bonus_counter
        profile.save()

        serializer.save(user=user, remarcacao=remarcacao_aluno)

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
        a_month = relativedelta(months=1)
        d_day = date(year, month, dia_pg)
        print(f'd_day ={d_day}')
        if dt.day < dia_pg:
            start_date = d_day - a_month
            end_date = d_day
            print(f'end_date = {end_date}')
            print(f'start_date = {start_date}')
        else:
            start_date = d_day
            end_date = d_day + a_month
            print(f'end_date = {end_date}')
            print(f'start_date = {start_date}')

        qs = Evento.objects.filter(user=u).filter(starting_date__gte=start_date,
                                                  starting_date__lt=end_date, historico=False)

        return Response({"eventos": EventoListSerializer(qs, many=True).data})


class EventoListAllAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        dt = date.today() - timedelta(5)
        data_inicial = self.request.GET.get("data_inicial")
        data_final = self.request.GET.get("data_final")

        if data_final and data_inicial:

            queryset_list = Evento.objects.filter(user__is_active=True, starting_date__range=[
                data_inicial, data_final])
            experimental = Experimental.objects.filter(starting_date__range=[
                data_inicial, data_final])
        else:
            queryset_list = Evento.objects.filter(user__is_active=True, starting_date__gte=dt)[
                :900]
            experimental = Experimental.objects.filter(starting_date__gte=dt)

        lista_final = []
        for a in experimental:
            resultado = {}
            resultado['starting_date'] = a.starting_date
            resultado['first_name'] = a.nome
            resultado['experimental'] = True
            lista_final.append(resultado)
        for a in queryset_list:
            resultado = {}
            resultado['starting_date'] = a.starting_date
            resultado['first_name'] = a.user.first_name
            resultado['desmarcado'] = a.desmarcado
            resultado['remarcacao'] = a.remarcacao
            resultado['reposicao'] = a.reposicao
            resultado['historico'] = a.historico
            resultado['bonus'] = a.bonus
            resultado['updated'] = a.updated
            resultado['experimental'] = False
            lista_final.append(resultado)
        # if list:
        # result_list = list(chain(expe, queryset_list))
        # print(f'lista_final = {lista_final}')

        # result_list = list(chain(queryset_list, experimental))
        # print(f'result_list = {result_list}')
        # json = serialize('json', result_list)
        # print(f'json = {json}')
        return queryset_list


@api_view(['GET'])
def listar_eventos_com_experimentais(request):
    print('antes')

    dt = date.today() - timedelta(5)
    data_inicial = request.GET.get("data_inicial")
    data_final = request.GET.get("data_final")

    if data_final and data_inicial:
        print(f'data  final ={data_final}')

        queryset_list = Evento.objects.filter(user__is_active=True, starting_date__range=[
            data_inicial, data_final])  # filter(user=self.request.user)
        experimental = Experimental.objects.filter(starting_date__range=[
            data_inicial, data_final])
    else:
        queryset_list = Evento.objects.filter(user__is_active=True, starting_date__gte=dt)[
            :900]
        experimental = Experimental.objects.filter(starting_date__gte=dt)

    lista_final = []
    for a in experimental:
        resultado = {}
        resultado['starting_date'] = a.starting_date
        resultado['first_name'] = a.nome
        resultado['experimental'] = True
        lista_final.append(resultado)
    for a in queryset_list:
        resultado = {}
        resultado['starting_date'] = a.starting_date
        resultado['first_name'] = a.user.first_name
        resultado['desmarcado'] = a.desmarcado
        resultado['remarcacao'] = a.remarcacao
        resultado['reposicao'] = a.reposicao
        resultado['historico'] = a.historico
        resultado['bonus'] = a.bonus
        resultado['updated'] = a.updated
        resultado['experimental'] = False
        lista_final.append(resultado)
    # if list:
    # result_list = list(chain(expe, queryset_list))
    print(f'lista_final = {list(lista_final)}')
    return Response({
        "lista": list(lista_final)
    })

#     return Response({"message": "Todas Aulas Deletadas"})


class EventoDesmarcadosListAllAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]

    def get_queryset(self, *args, **kwargs):
        dt = date.today() - timedelta(30)
        queryset_list = Evento.objects.filter(
            starting_date__gte=dt, desmarcado=True, remarcacao=True)
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
    Evento.objects.filter(
        user=user, starting_date__gte=datetime.now()).delete()

    ev = Evento.objects.filter(
        user=user, starting_date__lte=datetime.now())

    for aula in ev:
        aula.historico = True
        aula.save()

    return Response({"message": "Todas Aulas Deletadas"})


# @register_job(scheduler, trigger='cron', hour='3', minute='15', replace_existing=True)
# def enviar_parabens():
#     usuarios = Profile.objects.all()
#     now = datetime.now(timezone.utc)
#     month = now.month
#     day = now.day

#     tomorrow = now + timedelta(days=1)
#     print(f'day= {day}')
#     print(f'month= {month}')
#     print(f'tomorrow= {tomorrow}')
#     print(f'tomorrow.day= {tomorrow.day}')
#     print(f'tomorrow.month= {tomorrow.month}')
#     aniversariantes_hj = Profile.objects.filter(
#         data_nascimento__day=day).filter(data_nascimento__month=month)

#     aniversariantes_amanha = Profile.objects.filter(
#         data_nascimento__day=tomorrow.day).filter(data_nascimento__month=tomorrow.month)

#     print(f'aniversarioantes hj = {aniversariantes_hj}')
#     print(f'aniversarioantes amanha = {aniversariantes_amanha}')

#     for a in aniversariantes_hj:
#         print(f'a.data_nascimento =  {a.data_nascimento}')
#         subject = 'Studio Natalia Secchi Deseja Feliz Aniversario'
#         message = f"Feliz aniversario {a.user.first_name}."
#         from_email = settings.EMAIL_HOST_USER
#         to_list = [a.user.email]
#         send_mail(subject, message, from_email,
#                   to_list, fail_silently=False)
#     for b in aniversariantes_amanha:
#         print(f'b.data_nascimento =  {b.data_nascimento}')
#         subject = 'AVISO DE ANIVERSARIANTE AMANHA!'
#         message = f"Aluno {a.user.first_name}. vai fazer aniversario amanha!"
#         from_email = settings.EMAIL_HOST_USER
#         to_list = ["nataliasecchi@hotmail.com"]
#         send_mail(subject, message, from_email,
#                   to_list, fail_silently=False)


@api_view(['POST'])
def repor_aula(request):
    alunoId = request.data['alunoId']
    data = request.data['data']
    print(f'alunoId ={alunoId}')
    print(f'data ={data}')
    user = User.objects.get(id=alunoId)
    dia_pg = user.profile.dia_pagamento
    now = datetime.now(timezone.utc)
    dt = date.today()
    month = now.month
    year = now.year

    status = 0
    resposta = "Alguma coisa"
    a_month = relativedelta(months=1)
    d_day = date(year, month, dia_pg)
    print(f'd_day ={d_day}')
    if dt.day < dia_pg:
        start_date = d_day - a_month
        end_date = d_day
        print(f'end_date = {end_date}')
        print(f'start_date = {start_date}')
    else:
        start_date = d_day
        end_date = d_day + a_month
        print(f'end_date = {end_date}')
        print(f'start_date = {start_date}')

    print(f' acima aulas_do_mes')
    print(f'start_date ={start_date}')
    print(f'end_date ={end_date}')
    aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                          starting_date__lt=end_date, remarcacao=True, reposicao=False,  historico=False)
    print(f'aulas_do_mes = {aulas_do_mes}')

    aluno_reposicao = user.profile.aulas_reposicao
    print(f'aluno_reposicao = {aluno_reposicao}')
    # verificar se tem aula pra repor e se nao ja repos
    if aulas_do_mes.count() > aluno_reposicao:
        print(f'dentro do count > aluno_reposicao')
        # verificar se a data selecionada esta no mes atual do usuario
        count = Evento.objects.filter(
            user__profile__professor=user.profile.professor, starting_date=data).count()

        # if data > start_date and data < end_date:
        # if data > start_date and data < end_date:
        print(f'dentro do data do periodo do aluno')
        # verificar se existe aula nesse horario e no dia
        if count > 3:

            resposta = "Nao ha vagas nesse horario!"
            status = 403
            pass
        else:
            Evento.objects.create(user=user, starting_date=data, remarcacao=False, reposicao=True,
                                  desmarcado=False, bonus=True)
            resposta = "Aula remarcada com sucesso!"
            status = 200

        pass
        # else:
        #     resposta = "Data selecionada nao esta dentro do seu mes, escolha outra data!"
    else:
        status = 403
        resposta = "Voce nao tem aulas para remarcar este mes!"

    return Response({"message": resposta, "status": status})
