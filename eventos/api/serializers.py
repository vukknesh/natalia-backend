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

    class Meta:
        model = Evento
        fields = ['comentario', 'starting_date', 'ending_date']


class EventoDetailSerializer(ModelSerializer):

    user = UserSerializer(read_only=True)

    user_image = ImageField(source='user.profile.image', read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id', 'slug', 'comentario', 'starting_date', 'ending_date', 'user'

        ]

    def get_html(self, obj):
        return obj.get_markdown()


class EventoListSerializer(ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Evento
        fields = ['id', 'comentario', 'starting_date',
                  'ending_date', 'user', 'slug', ]
