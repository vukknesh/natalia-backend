from django.contrib import admin

# Register your models here.
from .models import Pagamento, AulaAvulsaGrupo, AulaExperimental, AulaPersonal, ResumoMensal
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'pago', 'plano_pagamento', 'valor')
    list_editable = ('pago', 'plano_pagamento', 'valor',)
    list_filter = ('pago', 'user', )

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Pagamento, ExtraAdmin)
admin.site.register(AulaExperimental)
admin.site.register(AulaAvulsaGrupo)
admin.site.register(AulaPersonal)
admin.site.register(ResumoMensal)
