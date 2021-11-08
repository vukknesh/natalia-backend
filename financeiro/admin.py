from django.contrib import admin

# Register your models here.
from .models import Pagamento, AulaAvulsaGrupo, AulaExperimental, AulaPersonal, ResumoMensal, VendaItems, Item, DespesasFixa, Teste, Experimental, ResumoManualMes, Despesas
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'pago', 'plano_pagamento', 'valor')
    list_editable = ('pago', 'plano_pagamento', 'valor',)
    list_filter = ('pago', 'user', )

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


class ExtraResumoAdmin(admin.ModelAdmin):
    list_display = ('data', 'despesas_do_mes',)
    list_filter = ('data', )

    # def despesas(self, obj):
    #     return self.despesas_do_mes


admin.site.register(Pagamento, ExtraAdmin)
admin.site.register(AulaExperimental)
admin.site.register(AulaAvulsaGrupo)
admin.site.register(AulaPersonal)
# admin.site.register(ResumoMensal)
admin.site.register(Item)
# admin.site.register(DespesasFixa)
admin.site.register(VendaItems)
admin.site.register(Teste)
admin.site.register(Experimental)
admin.site.register(Despesas)
admin.site.register(ResumoManualMes, ExtraResumoAdmin)
