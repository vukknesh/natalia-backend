from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField
)


from accounts.serializers import UserSerializer

from eventos.models import Evento


class EventoCreateUpdateSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id',  'comentario', 'user',
                  'desmarcado', 'remarcacao', 'reposicao', 'updated', 'historico', 'extra', 'atestado']


class EventoDetailSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id',  'comentario', 'bonus', 'extra',
                  'starting_date', 'user', 'desmarcado', 'remarcacao', 'reposicao', 'updated', 'historico', 'atestado']


class EventoListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id', 'comentario', 'starting_date', 'bonus', 'remarcacao', 'reposicao',
                  'user',  'desmarcado', 'updated', 'historico', 'extra', 'atestado']


class EventoListAllSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = CharField(source="user.first_name")
    plano = CharField(source="user.profile.plano")

    class Meta:
        model = Evento
        fields = ['id', 'comentario', 'extra', 'starting_date', 'bonus', 'remarcacao', 'reposicao',
                  'user',  'desmarcado', 'first_name', 'plano', 'updated', 'historico', 'atestado']
