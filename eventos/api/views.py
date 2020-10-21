from django.db.models import Q

from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from calendar import monthrange
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
from calendar import monthrange
from rest_framework.decorators import api_view
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
        data = datetime.now()
        if self.request.data['starting_date']:
            data = self.request.data['starting_date']
        if self.request.data['user']:

            user = User.objects.get(id=self.request.data['user'])
        else:
            user = self.request.user
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

    response_text = "Ok"
    dt = date.today()
    bonus_counter = user.profile.bonus_remarcadas
    aulas_counter = user.profile.aulas_remarcadas

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

    if(dif_hours <= 0):
        print('dentro')

        response_text = "Você só poderá remarcar aulas 3 horas antes."

    dia_pg = user.profile.dia_pagamento
    month_mais = month + 1
    month_menos = month - 1

    if month_mais == 13:
        month_mais = 1
        year = year + 1

    if month_menos == 0:
        month_menos = 12
        year = year - 1

    if dt.day < dia_pg:
        start_date = f'{year}-{month_menos}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
    else:
        start_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month_mais}-{dia_pg}T00:00:00Z'

    aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                          starting_date__lt=end_date, reposicao=False)

    print(f'aulas_do_mes {aulas_do_mes}')
    # teste

    if(user.profile.plano == "4 Aulas"):

        if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas == 0):
            response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
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
            response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
            bonus_counter = bonus_counter + 1
            pass
        if(aulas_bonus == 2 and user.profile.bonus_remarcadas <= 2):
            response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
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

        if(dif_hours <= 0):
            print('dentro')

            response_text = "Você só poderá remarcar aulas 3 horas antes."
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
        print('dentro do perform_update')

        now = datetime.now(timezone.utc)
        evento = self.get_object()
        year = now.year
        dt = date.today()
        month = now.month
        diff = evento.starting_date - now
        # duration_in_s = diff.total_seconds()
        # print(f'duration in s = {duration_in_s}')
        days, seconds = diff.days, diff.seconds
        dif_hours = days * 24 + seconds
        print(f'dif_hours update = {dif_hours}')
        response_text = "Ok"
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

            # msm dia que evento matutino
            if(now.date() == evento.starting_date.date()):
                print(f'same date')

            pass
        # funcionando

        if(dif_hours <= 0):
            print('dentro')

        dia_pg = user.profile.dia_pagamento
        month_mais = month + 1
        month_menos = month - 1
        if month_menos == 0:
            month_menos = 12
            year = year - 1

        if month_mais == 13:
            month_mais = 1
            year = year + 1
        if dt.day < dia_pg:
            start_date = f'{year}-{month_menos}-{dia_pg}T00:00:00Z'
            end_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
        else:
            start_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
            end_date = f'{year}-{month_mais}-{dia_pg}T00:00:00Z'

        aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                              starting_date__lt=end_date, reposicao=False)
        print(f'aulas_do_mes update {aulas_do_mes}')
        # aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
        #                                       starting_date__month__gte=month,
        #                                       starting_date__year__lte=year,
        #                                       starting_date__month__lte=month)
        # aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
        #                                      starting_date__month__gte=month,
        #                                      starting_date__year__lte=year,
        #                                      starting_date__month__lte=month)

        if(user.profile.plano == "4 Aulas"):
            aulas_bonus = aulas_do_mes.count() - 4
            if(aulas_do_mes.count() > 4 and user.profile.bonus_remarcadas == 0):
                response_text = 'Esta aula é uma aula bônus e não poderá ser remarcada!'
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

                response_text = "Você já remarcou 3 aulas deste mês."

            if(dif_hours <= 0):
                print('dentro')

                response_text = "Você só poderá remarcar aulas 3 horas antes."
        # deixar em cima do profile.bonus_remarcadas se nao conta errado!
        # if aulas_bonus > user.profile.bonus_remarcadas:
        #     print(f'aulas_bonus > = {aulas_bonus}')
        #     remarcacao_aluno = False
        # else:
        #     print(f'aulas_bonus < = {aulas_bonus}')

        #     remarcacao_aluno = True
        if aulas_bonus == user.profile.bonus_remarcadas:
            remarcacao_aluno = True
        else:
            remarcacao_aluno = False

        profile = user.profile
        profile.aulas_remarcadas = aulas_counter
        profile.bonus_remarcadas = bonus_counter

        profile.save()
        print(f'finalizou com perfil salvo + 1 {profile.aulas_remarcadas}')

        print(f'evento PERFORM_UPDATE= {evento}')
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
        month_mais = month + 1

        if month_mais == 13:
            month_mais = 1
            year = year + 1

        if dt.day < dia_pg:
            start_date = dt
            end_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
        else:
            start_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
            end_date = f'{year}-{month_mais}-{dia_pg}T00:00:00Z'

        print(f'start_date  {start_date}')
        print(f'end_date  {end_date}')
        # qs = Evento.objects.filter(starting_date__gte=datetime.now(), starting_date__year__gte=year,
        #                           starting_date__month__gte=month, starting_date__year__lte=year, starting_date__month__lte=month)
        # queryset_list = Evento.objects.filter(
        #     user=u).filter(starting_date__gte=dt, starting_date__year__gte=year,
        #                    starting_date__month__gte=month, starting_date__day__gte=dia_pg, starting_date__year__lte=year, starting_date__month__lte=month_mais, starting_date__day__lt=dia_pg)
        qs = Evento.objects.filter(user=u).filter(starting_date__gte=start_date,
                                                  starting_date__lt=end_date)

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

    return Response({"message": "Todas Aulas Deletadas"})


@api_view(['GET'])
def enviar_parabens():
    usuarios = User.objects.all()
    now = datetime.now(timezone.utc)

    for user in usuarios:

        if user.profile.data_nascimento:
            data = date(now.year, user.profile.data_nascimento.month,
                        user.profile.data_nascimento.day)
            data_menos_um = data - timedelta(1)
            if now.date() == data.date():
                subject = 'Studio Natalia Secchi Deseja Feliz Aniversario'
                message = f"Feliz aniversario {user.first_name}. \n \n https://www.murukututu.com/confirm_email/userf87dsafhdsfandjsa7fda6{user.id} \n \n Natalia Secchi!"
                from_email = settings.EMAIL_HOST_USER
                to_list = [user.email]
                send_mail(subject, message, from_email,
                          to_list, fail_silently=False)

            elif data_menos_um.date() == now.date():
                subject = 'Informe de aniversario de aluno'
                message = f" {user.first_name}. \n \n faz aniversario no dia {user.profile.data_nascimento} \n \n Natalia Secchi!"
                from_email = settings.EMAIL_HOST_USER
                to_list = ["leomcn@hotmail.com"]
                send_mail(subject, message, from_email,
                          to_list, fail_silently=False)
            else:
                subject = 'Nenhum aniversario'
                message = f" {user.first_name}. \n \n faz aniversario no dia {user.profile.data_nascimento} \n \n Natalia Secchi!"
                from_email = settings.EMAIL_HOST_USER
                to_list = ["leomcn@hotmail.com"]
                send_mail(subject, message, from_email,
                          to_list, fail_silently=False)


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
    month_mais = month + 1
    month_menos = month - 1
    resposta = "Alguma coisa"
    if month_menos == 0:
        month_menos = 12
        year = year - 1

    if month_mais == 13:
        month_mais = 1
        year = year + 1

    if dt.day < dia_pg:
        print(f'dt < dia_pg')
        start_date = f'{year}-{month_menos}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
    else:
        print(f'dt > dia_pg')
        start_date = f'{year}-{month}-{dia_pg}T00:00:00Z'
        end_date = f'{year}-{month_mais}-{dia_pg}T00:00:00Z'

    print(f' acima aulas_do_mes')
    aulas_do_mes = user.evento_set.filter(starting_date__gte=start_date,
                                          starting_date__lt=end_date, remarcacao=True, reposicao=False)
    print(f'aulas_do_mes = {aulas_do_mes}')

    aluno_reposicao = user.profile.aulas_reposicao
    print(f'aluno_reposicao = {aluno_reposicao}')
    # verificar se tem aula pra repor e se nao ja repos
    if aulas_do_mes.count() > aluno_reposicao:
        # verificar se a data selecionada esta no mes atual do usuario
        if data.date() > start_date.date() and data.date() < end_date.date():
            print(f'dentro do data do periodo do aluno')
            # verificar se existe aula nesse horario e no dia
            if Evento.objects.filter(starting_date__gte=now, starting_date__lt=end_date).exists():
                print(f'existe()')
                resposta = "Aula ja existe"
                pass
            else:
                Evento.objects.create(user=user, starting_date=data, remarcacao=False, reposicao=True,
                                      desmarcado=False, bonus=True)
                resposta = "Aula remarcada com sucesso!"

            pass
        else:
            resposta = "Data selecionada nao esta dentro do seu mes, escolha outra data!"

    return Response({"message": resposta})

# ####alteracoes
# aluno marcar propria reposicao

# deletar apenas de hj pra frente! ok
# aula reposicao AZUL ok
# quando aluno desmarcar aula, horario que desmarcou ok
# mudar cor no aplicativo de aula desmarcada que precisa repor ou nao ok
# pagamento automatico quando alterar plano e dia de pagamento ok
# mandar email um dia antes pra natalia, e mandar parabens pro aniversariante! ok
# mensagem ultima aula do mes nao pode ser remarcada!
