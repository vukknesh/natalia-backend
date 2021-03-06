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
                  'desmarcado', 'remarcacao', 'reposicao', 'updated', 'historico']


class EventoDetailSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id',  'comentario', 'bonus',
                  'starting_date', 'user', 'desmarcado', 'remarcacao', 'reposicao', 'updated', 'historico']


class EventoListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id', 'comentario', 'starting_date', 'bonus', 'remarcacao', 'reposicao',
                  'user',  'desmarcado', 'updated', 'historico']


class EventoListAllSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = CharField(source="user.first_name")
    plano = CharField(source="user.profile.plano")

    class Meta:
        model = Evento
        fields = ['id', 'comentario', 'starting_date', 'bonus', 'remarcacao', 'reposicao',
                  'user',  'desmarcado', 'first_name', 'plano', 'updated', 'historico']
