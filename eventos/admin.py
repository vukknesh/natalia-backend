from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Evento
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'desmarcado', 'bonus', 'remarcacao', 'starting_date', 'updated'
                    )
    list_editable = ('desmarcado', 'bonus', 'remarcacao')
    # list_filter = ('desmarcado', 'user', 'bonus', 'remarcacao')
    search_fields = ('user__first_name', )
    list_filter = (
        ('starting_date', DateRangeFilter), ('updated', DateTimeRangeFilter),
    )

    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Evento, ExtraAdmin)
