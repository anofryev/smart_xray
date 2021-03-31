from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.db import models
from django.contrib.auth.models import User
from urllib.request import urlretrieve, urlopen

class Practitioner(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100, null=True)
    given = models.CharField("Имя", max_length=100, null=True)
    family = models.CharField("Фамилия", max_length=100, null=True)



class Patient(models.Model):

    identifier = models.CharField("Идентификатор", max_length=100, null=True)
    given = models.CharField("Имя", max_length=100, null=True)
    family = models.CharField("Фамилия", max_length=100, null=True)



class ImagingStudy(models.Model):
    uid = models.CharField("UID", max_length=100, default="urn:oid:1.2.3.4.5")
    identifier = models.CharField("Идентификатор", max_length=100, null=True)
    date = models.CharField("Дата исследования", max_length = 50, null=True)
    numberOfSeries = models.PositiveIntegerField("Количество серий", null=True)
    numberOfInstances = models.PositiveIntegerField("Количество снимков", null=True)
    reference = models.CharField("Ссылка", max_length=1000 , null=True)
    description = models.CharField("Описание", max_length=2000, null=True)
    patient = models.ForeignKey(Patient, verbose_name= "Пациент", on_delete=models.SET_NULL, null=True)
    practitioner = models.ForeignKey(Practitioner, verbose_name="Специалист", on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, verbose_name="Пользователь", on_delete=models.CASCADE)

    def __str__(self):
        return self.uid


class Series(models.Model):
    uid = models.CharField("UID", max_length=100, default="urn:oid:1.2.3.4.5")
    date = models.CharField("Дата исследования", max_length=50, null=True)
    numberOfInstances = models.PositiveIntegerField("Количество снимков", null=True)
    reference = models.CharField("Ссылка", max_length=1000, null=True, blank=True)
    description = models.CharField("Описание", max_length=2000, null=True, blank=True)
    imaging_study = models.ForeignKey(ImagingStudy, verbose_name="Исследование", on_delete=models.CASCADE)
    dicom_file = models.FileField("DICOM Файл", upload_to="dicoms/", null=True, blank=True)
    image_field = models.ImageField("Изображение", upload_to="series/images", null=True, blank=True)

    def __str__(self):
        return self.uid

    def get_remote_dicom(self):
        serie = Series.objects.get(pk=self.pk)
        url = str(self.reference)
        file_temp = NamedTemporaryFile()
        file_temp.write(urlopen(url).read())
        file_temp.flush()

        serie.dicom_file.save("file_%s" % serie.pk, File(file_temp))
        serie.save()

    def get_remote_image(self):
        serie = Series.objects.get(pk=self.pk)
        url = str(self.reference)
        img_temp = NamedTemporaryFile()
        img_temp.write(urlopen(url).read())
        img_temp.flush()
        serie.image_field.save("image_%s" % serie.pk, File(img_temp))
        serie.save()


class Instance(models.Model):
    uid = models.CharField("UID", max_length=100, default="urn:oid:1.2.3.4.5")
    number = models.CharField("Идентификатор", max_length=100)
    date = models.CharField("Дата исследования", max_length=50, null=True)
    title = models.CharField("Описание", max_length=2000, null=True)
    image = models.ImageField("Изображение", upload_to="instances/", null=True)
    series = models.ForeignKey(Series, verbose_name="Серия", on_delete=models.CASCADE)



class Data(models.Model):
    title = models.CharField("Название", max_length=50,)
    image = models.ImageField("Изображение", upload_to="data/")