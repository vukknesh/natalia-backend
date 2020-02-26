from django.contrib import admin
from .models import Profile

# Register your models here.
# admin.site.register(Profile)


class MyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'plano', 'plano_pagamento',
                    'dia_pagamento', 'rg', 'cpf', 'telefone', 'endereco')
    list_editable = ('plano', 'plano_pagamento', 'dia_pagamento',
                     'rg', 'cpf', 'telefone', 'endereco',)
    list_filter = ('plano_pagamento', )

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Profile, ExtraAdmin)
