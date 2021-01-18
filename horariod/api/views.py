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
from horariod.models import Horario
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
    starting_date_string = request.data['starting_date']
    data_obj = datetime.strptime(starting_date_string, '%Y-%m-%d')
    # data_obj = datetime.strptime(starting_date_string, '%Y-%m-%d %H:%M:%S')
    print(f'starting_date_string ={starting_date_string}')
    print(f'data_obj ={data_obj}')
    dia_numerico = data_obj.weekday()
    print(f'dia_numerico ={dia_numerico}')
    horario_dict = Horario.objects.filter(
        user=user.profile.professor, weekday=dia_numerico)

    print(f'horario_dict = {horario_dict}')
    lista = []
    resultado = {}
    for ho in horario_dict:

        mytime = datetime.combine(data_obj, ho.hora_aula)
        count = Evento.objects.filter(
            user__profile__professor=prof, starting_date=mytime).count()

        if count > 3:
            resultado['hora'] = mytime
            resultado['count'] = count
            resultado['bool'] = False
            lista.append(resultado)
            print(lista)
            print(f'aula do dia {starting_date} tem {count} alunos ja')
        else:
            resultado['hora'] = mytime
            resultado['count'] = count
            resultado['bool'] = False
            lista.append(resultado)
            print(lista)
            print(f'aula disponivel do dia {starting_date}')

    return Response({"lista": lista})


@api_view(['POST'])
def get_horarios_disponiveis(request):
    u = request.data['user']
    user = User.objects.get(id=u)
    prof = user.profile.professor
    print(f'professor do usuario = {prof}')
    data = request.data['data']
    print(f'data = {data}')
    data_weekday = None
    horarios_professor = None
    if data:
        data_obj = datetime.strptime(data, '%Y-%m-%d')
        data_weekday = data_obj.weekday()
        print(f'data_weekday = {data_weekday}')
        disponiveis = Evento.objects.filter(
            starting_day__date=data, user__profile_professor=prof)
        # .values('starting_date').annotate(dcount=Count('starting_date'))
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
    queryset = Horario.objects.all()
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
