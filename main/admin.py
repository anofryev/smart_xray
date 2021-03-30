from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Practitioner, Patient, ImagingStudy, Series, Instance
# Register your models here.

admin.site.register(Practitioner)
admin.site.register(Patient)
admin.site.register(ImagingStudy)
admin.site.register(Instance)

@admin.register(Series)
class SeriesAdmin(admin.ModelAdmin):
    """Админка для серий"""
    list_display = ["uid", "date", "get_image"]

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image_field.url} width="50" height="60"')

    get_image.short_description = "Изображение"