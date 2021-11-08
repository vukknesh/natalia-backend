from rest_framework.fields import ReadOnlyField
from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    CharField,
    ImageField
)


from accounts.serializers import UserSerializer

from financeiro.models import Pagamento, ResumoMensal, AulaPersonal, AulaExperimental, AulaAvulsaGrupo, Item, VendaItems, DespesasFixa, Teste, Experimental, ResumoManualMes, Despesas


class PagamentoCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = Pagamento
        fields = "__all__"


class ExperimentalSerializer(ModelSerializer):

    class Meta:
        model = Experimental
        fields = "__all__"


class TesteSerializer(ModelSerializer):

    class Meta:
        model = Teste
        fields = "__all__"


class ItemCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = Item
        fields = "__all__"


class DespesaFixaCreateUpdateSerializer(ModelSerializer):

    class Meta:
        model = DespesasFixa
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


class ResumoManualMesListAllSerializer(ModelSerializer):
    despesas = SerializerMethodField()

    def get_despesas(self, obj):
        return self.despesas_set.objects.all()

    class Meta:
        model = ResumoManualMes
        readonly_fields = ['despesas_do_mes']
        fields = ['despesas', 'data', 'despesas_do_mes']


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
