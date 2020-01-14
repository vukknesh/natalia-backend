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
from datetime import date, timedelta

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
        plano = request.data['plano']
        dias = request.data['dias']
        horario = request.data['horario']

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        perfil = Profile.objects.get(user=user)
        print('perfil')
        perfil.plano = plano
        perfil.save()

        year = 2018
        date_object = date(year, 1, 1)
        date_object += timedelta(days=1-date_object.isoweekday())

        def daterange(start_date, end_date):
            for n in range(int((end_date - start_date).days)):
                yield start_date + timedelta(n)

        start_date = date(2013, 1, 1)
        end_date = date(2015, 6, 2)
        for single_date in daterange(start_date, end_date):
            print(single_date.strftime("%Y-%m-%d"))
        while date_object.year == year:
            print(date_object)
            date_object += timedelta(days=7)
        # if dias and horario:
        #     for(dia in range()):

        #           if date.dia.weekday() == 0: #  weekday (0 = Monday)
        #              print(f'dia = {dia}')
        #     Evento.objects.create()

        return Response({"message": "ok"})
