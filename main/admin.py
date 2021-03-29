from django.contrib import admin
from .models import Practitioner, Patient, ImagingStudy, Series, Instance
# Register your models here.

admin.site.register(Practitioner)
admin.site.register(Patient)
admin.site.register(ImagingStudy)
admin.site.register(Series)
admin.site.register(Instance)