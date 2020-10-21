from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Profile
from .serializers import UserSerializer, ProfileSerializer, ProfileUpdateSerializer, ProfessorSerializer
from .permissions import (
    IsOwnerOrReadOnly, IsAdminUserOrReadOnly, IsSameUserAllowEditionOrReadOnly
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_filters import rest_framework as filters
from rest_framework.decorators import api_view
from rest_framework.generics import (
    RetrieveUpdateAPIView,
    ListAPIView
)
from datetime import datetime, timezone
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView

import django_filters
from django.db.models import Q


class UserFilter(django_filters.FilterSet):
    multi_name_fields = django_filters.CharFilter(
        method='filter_by_all_name_fields')

    class Meta:
        model = User
        fields = []

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) | Q(last_name__icontains=value) | Q(
                username__icontains=value) | Q(email__icontains=value)
        )


class ProfileFilter(filters.FilterSet):
    multi_name_fields = django_filters.CharFilter(
        method='filter_by_all_name_fields')

    class Meta:
        model = Profile
        fields = []

    def filter_by_all_name_fields(self, queryset, name, value):
        return queryset.filter(
            Q(city__icontains=value) | Q(country__icontains=value) | Q(
                state__icontains=value)
        )


class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('first_name')
    serializer_class = UserSerializer
    filterset_class = UserFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsSameUserAllowEditionOrReadOnly,)


class ProfileViewSet(viewsets.ModelViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    filterset_class = ProfileFilter

    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)


class ProfessorListAllAPIView(ListAPIView):
    serializer_class = ProfessorSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, *args, **kwargs):

        queryset_list = Profile.objects.filter(
            is_professor=True)  # filter(user=self.request.user)

        return queryset_list


class ProfileUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileUpdateSerializer
    lookup_field = 'id'
    permission_classes = [IsOwnerOrReadOnly]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        # email send_email


class AniversariantesListApiView(ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self, *args, **kwargs):
        now = datetime.now(timezone.utc)
        month = now.month
        day = now.day
        print(f'day= {day}')
        print(f'month= {month}')
        queryset_list = Profile.objects.filter(
            data_nascimento__day=day).filter(data_nascimento__month=month)

        return queryset_list


# @api_view(['GET'])
# def get_aniversariantes(request):
#     now = datetime.now(timezone.utc)
#     month = now.month
#     day = now.day
#     print(f'day= {day}')
#     print(f'month= {month}')
#     aniversariantes = Profile.objects.filter(
#         data_nascimento__day=day).filter(data_nascimento__month=month)

#     print(f'aniversariantes = {aniversariantes}')

#     return Response({
#         "aniversariantes": ProfileSerializer(aniversariantes, many=True).data})
