from django.db.models.fields import FloatField
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


class DespesasSerializer(ModelSerializer):

    class Meta:
        model = Despesas
        fields = ("__all__")


class ResumoManualMesListAllSerializer(ModelSerializer):
    # despesas_do_mes = DespesasSerializer(many=True, read_only=True)
    despesas_do_mes = SerializerMethodField()
    total = SerializerMethodField()

    def get_despesas_do_mes(self, obj):
        d = obj.despesas_set.all()

        return DespesasSerializer(d, many=True).data

    def get_total(self, obj):
        t = 0
        for a in obj.despesas_set.all():
            t += a.valor

        return t

    class Meta:
        model = ResumoManualMes
        fields = ['id', 'data', 'despesas_do_mes', 'total']


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
