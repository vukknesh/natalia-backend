from rest_framework import serializers
from django.contrib.auth.models import User


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
    SlugField
)
from django.shortcuts import get_object_or_404
from .models import Profile


class UserSerializer(serializers.HyperlinkedModelSerializer):
    first_name = CharField(source='user.profile.first_name', read_only=True)

    class Meta:
        model = User
        depth = 1
        fields = ('url', 'id', 'username', 'first_name',
                  'email',)


class ProfileSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.ReadOnlyField(source='user.id')
    id = serializers.IntegerField(source='pk', read_only=True)

    slug = serializers.SlugField('slug', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.CharField(source='user.email', read_only=True)
    first_name = serializers.CharField(
        source='user.first_name', read_only=True)
    last_name = serializers.CharField(
        source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        depth = 1
        fields = ('all',)

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
    id = IntegerField(source='pk', read_only=True)
    slug = SlugField('slug', read_only=True)

    class Meta:
        model = Profile
        fields = ['all', ]
