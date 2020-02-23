from django.contrib import admin

# Register your models here.
from .models import Pagamento, AulaAvulsaGrupo, AulaExperimental, AulaPersonal, ResumoMensal
# Register your models here.
admin.site.register(Pagamento)
admin.site.register(AulaExperimental)
admin.site.register(AulaAvulsaGrupo)
admin.site.register(AulaPersonal)
admin.site.register(ResumoMensal)
