from django.contrib import admin

from .models import Horario
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'weekday', 'hora_aula')
    list_editable = ('weekday', 'hora_aula')
    list_filter = ('weekday', 'user', 'hora_aula')

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Horario, ExtraAdmin)
