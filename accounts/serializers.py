from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    ValidationError,
    Serializer,
    CharField,

    ReadOnlyField,
    ImageField
)
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


# User Serializer


class UserSerializer(ModelSerializer):
    profile_id = ReadOnlyField(source="profile.id")

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'profile_id', )

# Register Serializer


class RegisterSerializer(ModelSerializer):
    profile_id = ReadOnlyField(source="profile.id")

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password',
            'first_name',
            'profile_id',



        ]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):

        username = validated_data['username']
        email = validated_data['email']
        password = validated_data['password']

        first_name = validated_data['first_name']

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            password=validated_data['password']
        )

        return user

# Login Serializer


class LoginSerializer(Serializer):
    username = CharField()
    password = CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise ValidationError("Incorrect Credentials")
