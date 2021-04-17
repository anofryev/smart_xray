import fhirclient.models.imagingstudy as fhir_imagingstudy
import fhirclient.models.patient as fhir_patient
import fhirclient.models.practitioner as fhir_practitioner
from .models import Practitioner, Patient, ImagingStudy, Series, Instance, Data
import datetime
from wado.wado import WadoConnection # Dicom wado-rs соединение для загрузки соответствующих dicom файлов


def synchronizing(smart, request):
    print('now in synchronizing func')
    try:
        imaging_study_search = fhir_imagingstudy.ImagingStudy.where(struct={'modality': 'DX'}) # Ищем все ImagingStudy нужного типа
        imaging_studies = imaging_study_search.perform_resources(smart.server)
        for imaging_study in imaging_studies: # Перебираем все найденные ImagingStudies
            try:
                pull_wado(imaging_study, request) # Загрузка соответствующих Dicom
            except Exception as e:
                print(e)
            model_imaging_study = ImagingStudy()
            model_patient = Patient()
            model_practitioner = Practitioner()
            try: # ищем пациента
                print('Ищем пациента')
                patient_related = fhir_patient.Patient.read(imaging_study.patient.id, smart.server)
                model_patient.identifier = patient_related.id
                if patient_related.name[0].given:
                    model_patient.given = patient_related.name[0].given[0]
                if patient_related.name[0].family:
                    model_patient.family = patient_related.name[0].family
                if not Patient.objects.filter(identifier=model_patient.identifier).exists():
                    model_patient.save()
                else:
                    model_patient = Patient.objects.get(identifier=model_patient.identifier)
                    model_patient.save()
            except Exception as e:
                print('Ошибка нахождения пациента: {0}'.format(e))

            try: # ищем специалиста
                print('Ищем специалиста')
                practitioner_related = fhir_practitioner.Practitioner.read(imaging_study.referrer.id, smart.server)
                model_practitioner.identifier = practitioner_related.id
                if practitioner_related.name[0].given:
                    model_practitioner.given = practitioner_related.name[0].given[0]
                if practitioner_related.name[0].family:
                    model_practitioner.family = practitioner_related.name[0].family
                if not Practitioner.objects.filter(identifier=model_practitioner.identifier).exists():
                    model_practitioner.save()
                else:
                    model_practitioner = Practitioner.objects.get(identifier=model_practitioner.identifier)
            except Exception as e:
                print('Ошибка нахождения practitioner: {0}'.format(e))
            try: #Сохранение моделей в БД:
                print('Сохраняем модели в БД')
                model_imaging_study.identifier = imaging_study.identifier
                model_imaging_study.uid = imaging_study.uid
                model_imaging_study.patient = model_patient
                model_imaging_study.practitioner = model_practitioner
                model_imaging_study.date = str(datetime.datetime.now())
                if imaging_study.numberOfInstances:
                    model_imaging_study.numberOfInstances = int(imaging_study.numberOfInstances)
                if imaging_study.numberOfSeries:
                    model_imaging_study.numberOfSeries = int(imaging_study.numberOfSeries)
                if imaging_study.description:
                    model_imaging_study.description = imaging_study.description
                model_imaging_study.user = request.user
                if not ImagingStudy.objects.filter(uid=model_imaging_study.uid).exists():
                    model_imaging_study.save() # Сохраняем инстанс ImagingStudy, если в БД такой нет
                else: # Иначе получаем инстанс ImagingStudy из БД
                    model_imaging_study = ImagingStudy.objects.get(identifier=model_imaging_study.uid)
                for serie in imaging_study.series: # Далее для каждой серии в листе серий:
                    try:
                        print('Сохраняем серии')
                        model_serie = Series()
                        model_serie.uid = serie.uid
                        model_serie.date = str(datetime.datetime.now())
                        model_serie.imaging_study = model_imaging_study
                        if serie.description:
                            model_serie.description = serie.description
                        if serie.numberOfInstances:
                            model_serie.numberOfInstances = int(serie.numberOfInstances)
                        if not Series.objects.filter(uid=model_serie.uid).exists():
                            model_serie.save()  # Сохраняем модель, если в БД такой нет
                        else:  # Иначе получаем инстанс из БД
                            model_serie = Series.objects.get(uid=model_serie.uid)
                    except Exception as e:
                        print('Ошибка при создании серии: {0}'.format(e))
                    for instance in serie.instance: #В цикле по всем кадрам в листе кадров
                        try:
                            print('Сохраняем инстансы')
                            model_instance = Instance()
                            model_instance.series = model_serie
                            model_instance.uid = instance.uid
                            model_instance.number = instance.number
                            model_instance.date = str(datetime.datetime.now())
                            if instance.title:
                                model_instance.title = instance.title
                            if not Instance.objects.filter(uid=model_instance.uid).exists():
                                model_instance.save()  # Сохраняем модель, если в БД такой нет
                            pull_data(model_instance)
                        except Exception as e:
                            print('Ошибка при создании инстанса: {0}'.format(e))
            except Exception as e:
                print('Ошибка при сохранении моделей в БД: {0}'.format(e))

    except Exception as e:
        context = {'error': e}
        print("Ошибка в функции synchronizing:", e)
    print('Вышли из функции synchronization')
    return True

#Подтягивание соответствующих dicom

def pull_wado(study, request):
    try:
        state = request.session.get('state')
        connection = WadoConnection(
            hostname=study.endpoint,
            port="80",
            username=state.get('server').get('id_token'),
            password=state.get('server').get('access_token')
        )

        connection.download_wado_image(
            resource_parameters={"studyInstanceUID": study.uid, "objectUID": study.uid},
            folder="/data",
        )
    except Exception as e:
        print(e)




def pull_data(model_instance):
    data = Data.objects.get(title=model_instance.title)
    model_instance.image = data.image
    model_instance.save()