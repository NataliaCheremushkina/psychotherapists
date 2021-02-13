from django.contrib import admin
from .models import Therapist


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'name', 'photo', 'methods',)

    def has_add_permission(self, request):
        return False
