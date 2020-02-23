from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from django.conf import settings
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.serializers import AuthTokenSerializer
from userprofile.serializers import ProfileSerializer
from userprofile.models import Profile
from eventos.models import Evento
from datetime import datetime, date, timedelta, timezone
from rest_framework.decorators import api_view
from financeiro.models import Pagamento

# Register API


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    query_set = User.objects.all()

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "myprofile": ProfileSerializer(user.profile, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]

        })


# Login API


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(data=request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data

        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "myprofile": ProfileSerializer(user.profile, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserAPI(generics.RetrieveAPIView):
    model = User
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    # authentication_classes = (TokenAuthentication,)
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def retrieve(self, request, pk=None):
        profile = Profile.objects.filter(user=request.user.id)[0]

        return Response({
            "user": UserSerializer(request.user).data,
            "myprofile": ProfileSerializer(profile, context=self.get_serializer_context()).data,

        })


class RegisterWithPlano(generics.GenericAPIView):
    serializer_class = RegisterSerializer
    query_set = User.objects.all()

    def post(self, request, *args, **kwargs):

        plano = None
        professor = None
        professor_id = None
        dia_pagamento = None
        plano_pagamento = None
        if request.data['plano']:
            plano = request.data['plano']
        if request.data['plano_pagamento']:
            plano_pagamento = request.data['plano_pagamento']
        if request.data['dia_pagamento']:
            dia_pagamento = request.data['dia_pagamento']
        if request.data['professor_id']:
            professor_id = request.data['professor_id']
            professor = User.objects.get(id=professor_id)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        perfil = Profile.objects.get(user=user)
        print('perfil')
        perfil.plano = plano
        perfil.professor = professor
        perfil.dia_pagamento = dia_pagamento
        perfil.plano_pagamento = plano_pagamento
        # adicionar pagamentos no bancode dados
        perfil.save()
        add_pagamentos_por_aluno(user.id)

        return Response({"user": UserSerializer(user).data})


@api_view(['POST'])
def add_aulas_por_aluno(request):
    now = datetime.now(timezone.utc)
    print(f'now {now}')
    year = now.year
    print(f'year {year}')
    month = now.month
    print(f'month {month}')
    user = None
    aluno_id = None
    if request.data['alunoId']:
        aluno_id = request.data['alunoId']
        user = User.objects.get(id=aluno_id)

    horario = None
    if request.data['horario']:
        horario = request.data['horario']

    dias = None
    if request.data['dias']:
        dias = request.data['dias']

    if (dias and horario):
        print('dentro do if')
        date_object = date(year, month, 1)
        print(f'date_object {date_object}')
        date_object += timedelta(days=1-date_object.isoweekday())

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        start_date = date(year, month, 1)

        end_date = date(2025, 12, 30)
        tempo_horario = datetime.strptime(horario, '%H:%M:%S').time()
        for single_date in daterange(start_date, end_date):
            for dia in dias:

                if(single_date.weekday() == dia):

                    mydatetime = datetime.combine(
                        single_date, tempo_horario)
                    Evento.objects.create(
                        user=user, starting_date=mydatetime)
                    print('criado')
        while date_object.year == year:
            print(date_object)
            date_object += timedelta(days=7)

    return Response({"message": "OK"})


@api_view(['GET'])
def get_pagamentos_retroativo(request, user_id):
    add_pagamentos_por_aluno(user_id)
    return Response({"message": "Ok"})


def add_pagamentos_por_aluno(aluno_id):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month

    user = User.objects.get(id=aluno_id)
    print(f'user = {user.first_name}')
    dia = user.profile.dia_pagamento
    plano_pagamento = user.profile.plano_pagamento
    plano = user.profile.plano
    print(f'dia = {dia}')

    date_object = date(year, month, 1)
    date_object += timedelta(days=1-date_object.isoweekday())

    def daterange(start_date, end_date):
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    start_date = date(year, month, 1)

    end_date = date(2025, 12, 30)
    valor = 0
    # print(f'single_date = {single_date}')
    if (plano == "4 Aulas"):
        if(plano_pagamento == "Mensal"):
            valor = 180
        if(plano_pagamento == "Trimestral"):
            valor = 170
        if(plano_pagamento == "Semestral"):
            valor = 160
        if(plano_pagamento == "Anual"):
            valor = 150
    if (plano == "8 Aulas"):
        if(plano_pagamento == "Mensal"):
            valor = 300
        if(plano_pagamento == "Trimestral"):
            valor = 280
        if(plano_pagamento == "Semestral"):
            valor = 260
        if(plano_pagamento == "Anual"):
            valor = 240
    if (plano == "12 Aulas"):
        if(plano_pagamento == "Mensal"):
            valor = 420
        if(plano_pagamento == "Trimestral"):
            valor = 400
        if(plano_pagamento == "Semestral"):
            valor = 380
        if(plano_pagamento == "Anual"):
            valor = 360
    for single_date in daterange(start_date, end_date):

        if(single_date.day == dia):
            Pagamento.objects.get_or_create(
                user=user, data=single_date, valor=valor, plano_pagamento=plano_pagamento)
            # print(f'ifififif single_date = {single_date}')

    return Response({"message": "OK"})
