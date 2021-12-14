from django.db.models import Q

from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from dateutil.relativedelta import relativedelta
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
    u = request.data['user']
    user = User.objects.get(id=u)

    data = request.data['data']
    print(f'data = {data}')

    return Response({"horarios_disponiveis": horarios_professor,
                     "disponiveis": disponiveis})


@api_view(['POST'])
def get_horarios_disponiveis(request):
    print(f'request {request}')
    print(f'request.data {request.data}')
    u = request.data['user']
    user = User.objects.get(id=u)
    prof = user.profile.professor
    starting_date_string = request.data['starting_date']
    data_obj = datetime.strptime(starting_date_string, '%Y-%m-%d')
    # data_obj = datetime.strptime(starting_date_string, '%Y-%m-%d %H:%M:%S')
    print(f'starting_date_string ={starting_date_string}')
    print(f'data_obj ={data_obj}')
    dia_numerico = data_obj.weekday()
    print(f'dia_numerico ={dia_numerico}')
    horario_dict = Horario.objects.filter(
        user=prof, weekday=dia_numerico)

    print(f'horario_dict = {horario_dict}')
    lista = []
    for ho in horario_dict:
        resultado = {}

        mytime = datetime.combine(data_obj, ho.hora_aula)
        print(f'mytime {mytime}')
        # filter user_is_active
        count = Evento.objects.filter(user__is_active=True).filter(
            user__profile__professor=prof, starting_date=mytime).count()
        print(f'count = {count}')
        if count > 3:
            print('dentro > 3')
            resultado['hora'] = mytime
            resultado['count'] = count
            resultado['bool'] = False
            print(f'resultado dentro do count>3 ={resultado}')
            lista.append(resultado)
            print(lista)
        else:
            print('else > 3')
            resultado['hora'] = mytime
            resultado['count'] = count
            resultado['bool'] = True
            print(f'resultado fora do > 3 {resultado}')
            lista.append(resultado)
            print(lista)

    return Response({"lista": lista})


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
    prof = user.profile.professor
    status = 200
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
            user__profile__professor=prof, starting_date=data).count()

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


# ####alteracoes
# aluno marcar propria reposicao

# deletar apenas de hj pra frente! ok
# aula reposicao AZUL ok
# quando aluno desmarcar aula, horario que desmarcou ok
# mudar cor no aplicativo de aula desmarcada que precisa repor ou nao ok
# pagamento automatico quando alterar plano e dia de pagamento ok
# mandar email um dia antes pra natalia, e mandar parabens pro aniversariante! ok
# mensagem ultima aula do mes nao pode ser remarcada!
