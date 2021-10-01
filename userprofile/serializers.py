from rest_framework import serializers
from django.contrib.auth.models import User
from eventos.models import Evento
from dateutil.relativedelta import relativedelta
from eventos.api.serializers import EventoDetailSerializer
from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    BooleanField,
    ImageField,
    ValidationError,
    HyperlinkedModelSerializer,
    ReadOnlyField,
    IntegerField,
)
from django.shortcuts import get_object_or_404
from .models import Profile
from datetime import datetime, timezone, date


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile_id = ReadOnlyField(source="profile.id")

    class Meta:
        model = User
        depth = 1
        fields = ('id',  'username', 'first_name', 'profile_id',
                  'email',)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user_id = ReadOnlyField(source='user.id')
    first_name = CharField(source='user.first_name')
    email = CharField(source='user.email')
    ativo = BooleanField(source='user.is_active')
    aulas = SerializerMethodField()
    tem_bonus = SerializerMethodField()

    def get_tem_bonus(self, obj):
        now = datetime.now(timezone.utc)
        year = now.year
        month = now.month
        dt = date.today()
        dia_pg = obj.user.profile.dia_pagamento
        print(f'dia_pg get_tem_bonus {dia_pg}')
        print(f'obj.user.profile.plano get_tem_bonus {obj.user.profile.plano}')
        resp = 0

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

        aulas_do_mes = Evento.objects.filter_by_instance(obj).filter(starting_date__range=(
            start_date, end_date), reposicao=False, historico=False)
        print(f'aulas do mes get_tem_bonus = {aulas_do_mes}')
        print(f'aulas do mes.count() get_tem_bonus = {aulas_do_mes.count()}')
        if(obj.user.profile.plano == "4 Aulas" and aulas_do_mes.count() > 4):
            resp = aulas_do_mes.count() - 4
            print(
                f'dentro do obj.user.profile.plano count() = {aulas_do_mes.count()}')

        if(obj.user.profile.plano == "8 Aulas" and aulas_do_mes.count() > 8):
            resp = aulas_do_mes.count() - 8
        if(obj.user.profile.plano == "12 Aulas" and aulas_do_mes.count() > 12):
            resp = aulas_do_mes.count() - 12
        if(obj.user.profile.plano == "16 Aulas" and aulas_do_mes.count() > 16):
            resp = aulas_do_mes.count() - 16

        return resp

    def get_aulas(self, obj):
        c_qs = Evento.objects.filter_by_instance(
            obj).distinct('starting_date')[:30]
        aulas = EventoDetailSerializer(c_qs, many=True).data
        return aulas

    class Meta:
        model = Profile
        depth = 1
        fields = ('id', 'slug', 'ativo', 'data_nascimento', 'rg', 'plano_pagamento', 'profissao', 'estado_civil', 'telefone', 'is_professor', 'cpf', 'first_name', 'email', 'endereco', 'aulas', 'professor',
                  'aulas_remarcadas', 'bonus_remarcadas', 'plano', 'user_id', 'created_at', 'updated', 'tem_bonus')

    def get_full_name(self, obj):
        request = self.context['request']
        return request.user.get_full_name()

    def update(self, instance, validated_data):
        # First, update the User
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        # Then, update UserProfile

        for attr, value in validated_data.items():
            print(validated_data)
            setattr(instance, attr, value)
            instance.save()
        return instance


class ProfessorSerializer(serializers.HyperlinkedModelSerializer):
    user_id = ReadOnlyField(source='user.id')
    first_name = CharField(source='user.first_name')
    email = CharField(source='user.email')
    ativo = BooleanField(source='user.is_active')

    class Meta:
        model = Profile
        depth = 1
        fields = ('id', 'slug', 'ativo', 'data_nascimento', 'rg',   'cpf', 'first_name', 'email', 'endereco',
                  'user_id')

    def get_full_name(self, obj):
        request = self.context['request']
        return request.user.get_full_name()

    def update(self, instance, validated_data):
        # First, update the User
        user_data = validated_data.pop('user', {})
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)

        # Then, update UserProfile

        for attr, value in validated_data.items():
            print(validated_data)
            setattr(instance, attr, value)
            instance.save()
        return instance


class ProfileUpdateSerializer(ModelSerializer):
    user = ReadOnlyField(source='user.id')

    class Meta:
        model = Profile
        fields = ('id', 'slug', 'data_nascimento', 'rg', 'plano_pagamento', 'profissao', 'estado_civil', 'telefone', 'is_professor', 'cpf', 'first_name',  'endereco', 'aulas', 'professor',
                  'aulas_remarcadas', 'bonus_remarcadas', 'plano', 'user', 'created_at', 'updated')
