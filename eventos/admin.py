from django.contrib import admin

# Register your models here.
from .models import Evento
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'desmarcado', 'bonus', 'starting_date'
                    )
    list_editable = ('desmarcado', 'bonus',)
    list_filter = ('desmarcado', 'user', 'bonus', )

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Evento, ExtraAdmin)
