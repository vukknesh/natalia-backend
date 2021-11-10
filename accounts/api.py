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

class UsersActiveList(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, *args, **kwargs):
        queryset_list = User.objects.filter(
            is_active=True).order_by('first_name')

        return queryset_list


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
        print('dentro')
        plano = None
        professor = None
        professor_id = None
        dia_pagamento = None
        plano_pagamento = None
        cpf = None
        rg = None
        data_nascimento = None
        endereco = None
        profissao = None
        estado_civil = None
        telefone = None
        print('dps das variaveis')
        print(f'request.data = {request.data}')
        if request.data['profissao']:
            profissao = request.data['profissao']
        if request.data['estado_civil']:
            estado_civil = request.data['estado_civil']
        if request.data['endereco']:
            endereco = request.data['endereco']
        if request.data['telefone']:
            telefone = request.data['telefone']
        if request.data['cpf']:
            cpf = request.data['cpf']
        if request.data['rg']:
            rg = request.data['rg']
        if request.data['data_nascimento']:
            data_nascimento = request.data['data_nascimento']
        if request.data['plano']:
            plano = request.data['plano']
        if request.data['plano_pagamento']:
            plano_pagamento = request.data['plano_pagamento']
        if request.data['dia_pagamento']:
            dia_pagamento = request.data['dia_pagamento']
        if request.data['professor_id']:
            professor_id = request.data['professor_id']
            print('antes do professor')
            professor = User.objects.get(id=professor_id)

        print('aqui dps dos ifs')
        serializer = self.get_serializer(data=request.data)
        print('antes do is valid')
        serializer.is_valid(raise_exception=True)
        print('depois do is valid')
        user = serializer.save()
        perfil = Profile.objects.get(user=user)
        print('perfil')
        perfil.plano = plano
        perfil.professor = professor
        perfil.dia_pagamento = dia_pagamento
        perfil.plano_pagamento = plano_pagamento
        perfil.data_nascimento = data_nascimento
        perfil.rg = rg
        perfil.cpf = cpf
        perfil.endereco = endereco
        perfil.profissao = profissao
        perfil.estado_civil = estado_civil
        perfil.telefone = telefone
        # adicionar pagamentos no bancode dados
        perfil.save()
        add_pagamentos_por_aluno(user.id)

        return Response({"user": UserSerializer(user).data})


@api_view(['POST'])
def add_aulas_por_aluno(request):
    now = datetime.now(timezone.utc)
    if request.data['comecar']:
        now = request.data['comecar']
    print(f'now {now}')
    year = now.year
    print(f'year {year}')
    month = now.month
    print(f'month {month}')
    d = now.day
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

        start_date = date(year, month, d)

        end_date = date(2025, 12, 30)
        tempo_horario = datetime.strptime(horario, '%H:%M:%S').time()
        for single_date in daterange(start_date, end_date):
            for dia in dias:

                if(single_date.weekday() == dia):

                    mydatetime = datetime.combine(
                        single_date, tempo_horario)

                    Evento.objects.get_or_create(
                        user=user, starting_date=mydatetime)
                    print('criado')
        while date_object.year == year:
            print(date_object)
            date_object += timedelta(days=7)

    return Response({"message": "OK"})


@api_view(['GET'])
def get_pagamentos_retroativo(request, user_id):
    resposta = add_pagamentos_por_aluno(user_id)
    return Response({"message": resposta})


def add_pagamentos_por_aluno(aluno_id):
    now = datetime.now(timezone.utc)
    year = now.year
    month = now.month
    pagamentos_do_aluno = Pagamento.objects.filter(
        user_id=aluno_id, data__gte=now)
    print(f'pagamentos_do_aluno={pagamentos_do_aluno}')

    for pg in pagamentos_do_aluno:
        pg.delete()

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
    if (plano == "16 Aulas"):
        if(plano_pagamento == "Mensal"):
            valor = 560
        if(plano_pagamento == "Trimestral"):
            valor = 540
        if(plano_pagamento == "Semestral"):
            valor = 520
        if(plano_pagamento == "Anual"):
            valor = 500
    for single_date in daterange(start_date, end_date):
        print(f'single_date = {single_date}')

        if(single_date.day == dia):
            Pagamento.objects.get_or_create(
                user=user, data=single_date, valor=valor, plano_pagamento=plano_pagamento)
            # print(f'ifififif single_date = {single_date}')

    return "ok"
