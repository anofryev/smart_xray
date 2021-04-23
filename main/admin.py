from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Practitioner, Patient, ImagingStudy, Series, Instance, Data
# Register your models here.

admin.site.register(Practitioner)
admin.site.register(Patient)
admin.site.register(ImagingStudy)
admin.site.register(Instance)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Админка для серий"""
    list_display = ["uid", "date"]
