from django.contrib import admin
from rangefilter.filters import DateRangeFilter, DateTimeRangeFilter
from .models import Evento
# Register your models here.


class ExtraAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'desmarcado', 'bonus', 'remarcacao', 'starting_date'
                    )
    list_editable = ('desmarcado', 'bonus', 'remarcacao')
    # list_filter = ('desmarcado', 'user', 'bonus', 'remarcacao')
    list_filter = (
        ('starting_date', DateRangeFilter), ('updated', DateTimeRangeFilter),
    )

    # def get_rangefilter_starting_date_default(self, request):
    #     return (datetime.date.today, datetime.date.today)

    # # If you would like to change a title range filter
    # # method pattern "get_rangefilter_{field_name}_title"
    # def get_rangefilter_starting_date_title(self, request, field_path):
    #     return 'Aula'
    def get_name(self, obj):
        return "{}".format(obj.user.first_name)


admin.site.register(Evento, ExtraAdmin)
