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
        if request.data['plano']:
            plano = request.data['plano']

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        perfil = Profile.objects.get(user=user)
        print('perfil')
        perfil.plano = plano
        perfil.save()

        return Response({"user": UserSerializer(user).data})


@api_view(['POST'])
def add_aulas_por_aluno(request):
    now = datetime.now(timezone.utc)
    print(f'now {now}')
    year = now.year
    print(f'year {year}')
    month = now.month
    print(f'month {month}')
    aluno_id = None
    user = None
    if request.data['alunoId']:
        aluno_id = request.data['alunoId']
        user = User.objects.get(id=aluno_id)

    horario = None
    if request.data['horario']:
        horario = request.data['horario']
    ate_ano = None
    if request.data['ateAno']:
        ate_ano = request.data['ateAno']
    dias = None
    if request.data['dias']:
        dias = request.data['dias']

    if (dias and horario and ate_ano):
        print('dentro do if')
        date_object = date(year, month, 1)
        print(f'date_object {date_object}')
        date_object += timedelta(days=1-date_object.isoweekday())

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        start_date = date(year, month, 1)

        end_date = date(ate_ano, 12, 30)
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
