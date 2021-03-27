from django.db import models
from django.contrib.auth.models import User


class Practitioner(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100, null=True)
    given = models.CharField("Имя", max_length=100, null=True)
    family = models.CharField("Фамилия", max_length=100, null=True)

    def __str__(self):
        result = None
        if self.family:
            result += self.family
        if self.given:
            result += self.given
        return result


class Patient(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100, null=True)
    given = models.CharField("Имя", max_length=100, null=True)
    family = models.CharField("Фамилия", max_length=100, null=True)

    def __str__(self):
        result = None
        if self.family:
            result += self.family
        if self.given:
            result += self.given
        return result


class ImagingStudy(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100)
    date = models.CharField("Дата исследования", max_length = 50, null=True)
    numberOfSeries = models.PositiveIntegerField("Количество серий", null=True)
    numberOfInstances = models.PositiveIntegerField("Количество снимков", null=True)
    reference = models.CharField("Ссылка", max_length=1000 , null=True)
    description = models.CharField("Описание", max_length=2000, null=True)
    patient = models.ForeignKey(Patient, verbose_name= "Пациент", on_delete=models.SET_NULL, null=True)
    practitioner = models.ForeignKey(Practitioner, verbose_name="Специалист", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    def __str__(self):
        return self.identifier


class Series(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100)
    date = models.CharField("Дата исследования", max_length=50, null=True)
    numberOfInstances = models.PositiveIntegerField("Количество снимков", null=True)
    reference = models.CharField("Ссылка", max_length=1000, null=True)
    description = models.CharField("Описание", max_length=2000, null=True)
    imaging_study = models.ForeignKey(ImagingStudy, verbose_name="Исследование", on_delete=models.CASCADE)


class Instance(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100)
    date = models.CharField("Дата исследования", max_length=50, null=True)
    description = models.CharField("Описание", max_length=2000, null=True)
    image = models.ImageField("Изображение", upload_to="instances/", null=True)
    series = models.ForeignKey(Series, verbose_name="Серия", on_delete=models.CASCADE)
    reference = models.CharField("Ссылка", max_length=1000, null=True)



