from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField
)


from accounts.serializers import UserSerializer

from horario.models import Horario


class HorarioCreateUpdateSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id',  'dia', 'user',
                  'hora_aula']


class HorarioDetailSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id',  'dia',
                  'user', 'hora_aula']


class HorarioListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Horario
        fields = ['id', 'dia',
                  'user',  'hora_aula']


class HorarioListAllSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = CharField(source="user.first_name")

    class Meta:
        model = Horario
        fields = ['id', 'dia',
                  'user',  'hora_aula', 'first_name']
