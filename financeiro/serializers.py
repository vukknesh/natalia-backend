from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField
)


from accounts.serializers import UserSerializer

from financeiro.models import Pagamento, ResumoMensal, AulaPersonal, AulaExperimental, AulaAvulsaGrupo, Item, VendaItems


class PagamentoCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = Pagamento
        fields = "__all__"


class ItemCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = "__all__"


class VendaItemsCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = VendaItems
        fields = "__all__"


class PagamentoDetailSerializer(ModelSerializer):

    class Meta:
        model = Pagamento
        fields = "__all__"


class PagamentoListSerializer(ModelSerializer):
    first_name = CharField(source="user.first_name")

    class Meta:
        model = Pagamento
        fields = ['id', 'first_name', 'pago',
                  'data', 'valor', 'plano_pagamento']


class PagamentoListAllSerializer(ModelSerializer):
    first_name = CharField(source="user.first_name")

    class Meta:
        model = Pagamento
        fields = ['id', 'first_name', 'pago',
                  'data', 'valor', 'plano_pagamento']


class ResumoMensalListAllSerializer(ModelSerializer):

    class Meta:
        model = ResumoMensal
        fields = "__all__"


class AulaPersonalCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = AulaPersonal
        fields = "__all__"


class AulaExperimentalCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = AulaExperimental
        fields = "__all__"


class AulaAvulsaGrupoCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = AulaAvulsaGrupo
        fields = "__all__"
