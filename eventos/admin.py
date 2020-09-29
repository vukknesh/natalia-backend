from django.contrib import admin

# Register your models here.
from .models import Evento
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'desmarcado', 'bonus', 'remarcacao', 'starting_date'
                    )
    list_editable = ('desmarcado', 'bonus', 'remarcacao')
    list_filter = ('desmarcado', 'user', 'bonus', 'remarcacao')

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Evento, ExtraAdmin)
