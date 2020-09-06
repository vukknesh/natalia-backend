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
from datetime import datetime, timezone
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
        if(evento.desmarcado):
            raise ValidationError({"message": "Aula já desmarcada!"})
        if(evento.bonus):
            raise ValidationError(
                {"message": "Aula bônus não pode ser desmarcada!"})
        if(evento.starting_date.hour <= 12):
            # evento proximo dia
            if(now.hour >= 23 and ((evento.starting_date.day - now.day) == 1)):
                print(f'um dia anterior')
                raise ValidationError(
                    {"message": "Voce so pode remarcar aulas matutinas antes das 20hrs do dia anterior."})
            # msm dia que evento matutino
            if(now.date() == evento.starting_date.date()):
                print(f'same date')
                raise ValidationError(
                    {"message": "Voce so pode remarcar aulas matutinas antes das 20hrs do dia anterior."})
            pass
        # funcionando

        if(dif_hours <= 0):
            print('dentro')
            raise ValidationError(
                {"message": "Voce so pode remarcar aulas 3 horas antes."})

        aulas_do_mes = user.evento_set.filter(starting_date__year__gte=year,
                                              starting_date__month__gte=month,
                                              starting_date__year__lte=year,
                                              starting_date__month__lte=month)
        if(user.profile.plano == "4 Aulas"):
            if(user.profile.aulas_remarcadas > 0):
                raise ValidationError(
                    {"message": "Voce ja remarcou 1 aula deste mes."})
            if(aulas_do_mes.count() > 4):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass
        if(user.profile.plano == "8 Aulas"):
            if(user.profile.aulas_remarcadas > 1):
                raise ValidationError(
                    {"message": "Voce ja remarcou 2 aulas deste mes."})
            if(aulas_do_mes.count() > 8):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass

        if(user.profile.plano == "12 Aulas"):
            if(user.profile.aulas_remarcadas > 2):
                raise ValidationError(
                    {"message": "Voce ja remarcou 3 aulas deste mes."})
            if(aulas_do_mes.count() > 12):
                if(aulas_do_mes.last() == evento):
                    raise ValidationError(
                        {"message": "Essa aula é um bônus e não poderá ser remarcada!"})
                pass
        profile = user.profile
        profile.aulas_remarcadas = profile.aulas_remarcadas + 1
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
        if request.data['user_id'] is not None:
            u = User.objects.get(id=request.data['user_id'])
        else:
            u = User.objects.first()

        qs = Evento.objects.filter(starting_date__gte=datetime.now())
        queryset_list = Evento.objects.filter(
            user=u).filter(starting_date__gte=datetime.now())[:30]
        # .filter(starting_date__gte=datetime.now())  # filter(user=self.request.user)

        return Response({"eventos": EventoListSerializer(queryset_list, many=True).data})


class EventoListAllAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination

    def get_queryset(self, *args, **kwargs):
        queryset_list = Evento.objects.filter(starting_date__gte=datetime.now())[
            :900]  # filter(user=self.request.user)
        print(f'querylist = {queryset_list}')

        return queryset_list


class EventoByProfAPIView(ListAPIView):
    serializer_class = EventoListAllSerializer
    permission_classes = [AllowAny]
    pagination_class = LimitOffsetPagination
    page_size = 200

    def get_queryset(self, *args, **kwargs):

        queryset_list = Evento.objects.filter(
            user__profile__professor=self.request.user)  # filter(user=self.request.user)
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
