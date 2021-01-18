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
from horario.models import Horario
from eventos.models import Evento
from calendar import monthrange
from rest_framework.decorators import api_view
from .permissions import IsOwnerOrReadOnly

from .serializers import (
    HorarioCreateUpdateSerializer,
    HorarioDetailSerializer,
    HorarioListSerializer,
    HorarioListAllSerializer
)

import django_filters


# class HorarioFilter(filters.FilterSet):
#     multi_name_fields = django_filters.CharFilter(
#         method='filter_by_all_name_fields')

#     class Meta:
#         model = Horario
#         fields = []

#     def filter_by_all_name_fields(self, queryset, name, value):
#         return queryset.filter(
#             Q(city__icontains=value) | Q(address__icontains=value) | Q(
#                 state__icontains=value)
#         )


class HorarioCreateAPIView(CreateAPIView):
    queryset = Horario.objects.all()
    serializer_class = HorarioCreateUpdateSerializer
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


@api_view(['POST'])
def add_reposicao(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    starting_date = request.data['starting_date']
    print(f'starting_date ={starting_date}')
    dia_numerico = starting_date.weekday()
    print(f'dia_numerico ={dia_numerico}')
    horario_dict = Horario.objects.filter(
        user=user.profile.professor, dia=dia_numerico)

    print(f'horario_dict = {horario_dict}')

    if dia_numerico and horario_dict:
        pass


@api_view(['POST']):
def get_horarios_disponiveis:
    u = request.data['user']
    user = User.objects.get(id=u)
    prof = user.profile.professor
    print(f'professor do usuario = {prof}')
    data = request.data['data']
    print(f'data = {data}')
    data_weekday = None
    horarios_professor = None
    if data:
        data_weekday = data.weekday()
        print(f'data_weekday = {data_weekday}')
        disponiveis = Evento.objects.filter(
            starting_day__date=data, user__profile_professor=prof).values('starting_date').annotate(dcount=Count('starting_date'))
        print(f'disponiveis = {disponiveis}')
    if prof:
        horarios_professor = Horario.objects.filter(
            user=prof, dia=data_weekday)
        print(f'horarios_prof = {horarios_professor}')

    # Evento.objects.create(user=user, starting_date=starting_date, remarcacao=False, reposicao=True,
    #                           desmarcado=False, bonus=True)
    return Response({"horarios_disponiveis": horarios_professor,
                     "disponiveis": disponiveis})


class HorarioDetailAPIView(RetrieveAPIView):
    queryset = Horario.objects.filter(starting_date__gte=datetime.now())
    serializer_class = HorarioDetailSerializer
    lookup_field = 'id'
    permission_classes = [AllowAny]
    # lookup_url_kwarg = "abc"


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
    aulas_do_mes = user.Horario_set.filter(starting_date__gte=start_date,
                                           starting_date__lt=end_date, remarcacao=True, reposicao=False,  historico=False)
    print(f'aulas_do_mes = {aulas_do_mes}')

    aluno_reposicao = user.profile.aulas_reposicao
    print(f'aluno_reposicao = {aluno_reposicao}')
    # verificar se tem aula pra repor e se nao ja repos
    if aulas_do_mes.count() > aluno_reposicao:
        print(f'dentro do count > aluno_reposicao')
        # verificar se a data selecionada esta no mes atual do usuario

        # if data > start_date and data < end_date:
        # if data > start_date and data < end_date:
        print(f'dentro do data do periodo do aluno')
        # verificar se existe aula nesse horario e no dia
        if Horario.objects.filter(starting_date__hour__gte=now, starting_date__lt=end_date).exists():
            print(f'existe()')
            resposta = "Aula ja existe"
            pass
        else:
            Horario.objects.create(user=user, starting_date=data, remarcacao=False, reposicao=True,
                                   desmarcado=False, bonus=True)
            resposta = "Aula remarcada com sucesso!"

        pass
        # else:
        #     resposta = "Data selecionada nao esta dentro do seu mes, escolha outra data!"

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
