from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField
)


from accounts.serializers import UserSerializer

from horariod.models import Horario


class HorarioCreateUpdateSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id',   'user', 'weekday',
                  'hora_aula']


class HorarioDetailSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id', 'weekday',
                  'user', 'hora_aula']


class HorarioListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id', 'weekday',
                  'user',  'hora_aula']


class HorarioListAllSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = CharField(source="user.first_name")

    class Meta:
        model = Horario
        fields = ['id',
                  'user',  'hora_aula', 'weekday', 'first_name']
