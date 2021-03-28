import fhirclient.models.imagingstudy as imagingstudy
import fhirclient.models.patient as patient
import fhirclient.models.practitioner as practitioner
import models
import datetime


def synchronizing(smart, request):
    try:
        imaging_study_search = imagingstudy.ImagingStudy.where(struct={'modality': 'DX'}) # Ищем все ImagingStudy нужного типа
        imaging_studies = imaging_study_search.perform_resources(smart.server)
        for imaging_study in imaging_studies: # Перебираем все найденные ImagingStudies
            model_imaging_study = models.ImagingStudy()
            model_patient = models.Patient()
            model_practitioner = models.Practitioner()
            try: # ищем пациента
                patient_related = patient.Patient.read(imaging_study.patient.id)
                model_patient.identifier = patient_related.id
                if patient_related.given:
                    model_patient.given = patient_related.given
                if patient_related.family:
                    model_patient.family = patient_related.family
                if not models.Patient.objects.filter(identifier=model_patient.identifier).exists():
                    model_patient.save()
                else:
                    model_patient = models.Patient.objects.get(identifier=model_patient.identifier)
            except Exception as e:
                print('Ошибка нахождения пациента: {0}'.format(e))

            try: # ищем специалиста
                practitioner_related = practitioner.Practitioner.read(imaging_study.practitioner.id)
                model_practitioner.identifier = practitioner_related.id
                if practitioner_related.given:
                    model_practitioner.given = practitioner_related.given
                if practitioner_related.family:
                    model_practitioner.family = practitioner_related.family
                if not models.Practitioner.objects.filter(identifier=model_practitioner.identifier).exists():
                    model_practitioner.save()
                else:
                    model_practitioner = models.Practitioner.objects.get(identifier=model_practitioner.identifier)
            except Exception as e:
                print('Ошибка нахождения practitioner: {0}'.format(e))
            try: #Сохранение моделей в БД:
                model_imaging_study.identifier = imaging_study.id
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
                for serie in imaging_study.series: # Далее для каждой серии в листе серий:
                    try:
                        model_serie = models.Series()
                        model_serie.identifier = serie.identifier
                        model_serie.date = str(datetime.datetime.now())
                        model_serie.imaging_study = model_imaging_study
                        if serie.description:
                            model_serie.description = serie.description
                        if serie.numberOfInstances:
                            model_serie.numberOfInstances = int(serie.numberOfInstances)
                    except Exception as e:
                        print('Ошибка при создании серии: {0}'.format(e))
                    for instance in serie.instance: #В цикле по всем кадрам в листе кадров
                        try:
                            model_instance = models.Instance()
                            model_instance.number = instance.number
                            model_instance.date = str(datetime.datetime.now())
                            if instance.title:
                                model_instance.title = instance.title
                        except Exception as e:
                            print('Ошибка при создании инстанса: {0}'.format(e))

            except Exception as e:
                print('Ошибка при сохранении моделей в БД: {0}'.format(e))

    except Exception as e:
        context = {'error': e}
        print("Ошибка в функции synchronizing:", e)
    return True
