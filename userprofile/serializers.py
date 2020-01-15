from rest_framework import serializers
from django.contrib.auth.models import User
from eventos.models import Evento
from eventos.api.serializers import EventoDetailSerializer

from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField,
    ValidationError,
    HyperlinkedModelSerializer,
    ReadOnlyField,
    IntegerField,
)
from django.shortcuts import get_object_or_404
from .models import Profile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile_id = ReadOnlyField(source="user.profile.id")

    class Meta:
        model = User
        depth = 1
        fields = ('id',  'username', 'first_name', 'profile_id',
                  'email',)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = ReadOnlyField(source='user.id')
    first_name = CharField(source='user.first_name')
    email = CharField(source='user.email')
    aulas = SerializerMethodField()

    def get_aulas(self, obj):
        c_qs = Evento.objects.filter_by_instance(obj).distinct('starting_date')
        aulas = EventoDetailSerializer(c_qs, many=True).data
        return aulas

    class Meta:
        model = Profile
        depth = 1
        fields = ('id', 'slug', 'first_name', 'email', 'endereco', 'aulas',
                  'aulas_remarcadas', 'plano', 'user', 'created_at', 'updated')

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
        fields = ('user',
                  'aulas_remarcadas', 'plano',  'created_at', 'updated', 'endereco')
