from django.contrib import admin
from .models import Profile

# Register your models here.
# admin.site.register(Profile)


class MyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request, obj=None):
        return False


admin.site.register(Profile, MyAdmin)
