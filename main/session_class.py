import logging
from fhirclient import client
from fhirclient.models.medication import Medication
from fhirclient.models.medicationrequest import MedicationRequest


class Session:
    # Дефолтные настройки для SMART клиента
    smart_defaults = {
        'app_id': 'my_web_app',
        'api_base': 'http://localhost:4013/v/r3/sim/eyJoIjoiMSIsImoiOiIxIn0/fhir',
        'redirect_uri': 'http://localhost:8000/fhir-app/',
    }

    fhir_client = None
    state = None

    # Инициализация класса
    def __init__(self, request):
        self.request = request
        state = self.request.session.get('state')
        if state:
            self.smart = client.FHIRClient(state=state, save_func=self.save_state)
            print('state is: {0}'.format(state))
        else:
            self.smart = client.FHIRClient(settings=self.smart_defaults, save_func=self.save_state)
            print('no state, create new connection')

    def get_smart(self):
        state = self.request.session.get('state')
        if state:
            return client.FHIRClient(state=state, save_func=self.save_state)
        else:
            return client.FHIRClient(settings=smart_defaults, save_func=self.save_state)

    def save_state(self, state):
        self.request.session['state'] = state


    def logout(self):
        if 'state' in self.request.session:
            smart = self.get_smart()
            smart.reset_patient()

    def reset(self):
        if 'state' in self.request.session:
            del self.request.session['state']
            print('State deleted from session')

    def get_medication_by_ref(self, ref):
        med_id = ref.split("/")[1]
        return Medication.read(med_id, self.smart.server).code

    def get_prescriptions(self):
        bundle = MedicationRequest.where({'patient': self.smart.patient_id}).perform(self.smart.server)
        pres = [be.resource for be in bundle.entry] if bundle is not None and bundle.entry is not None else None
        if pres is not None and len(pres) > 0:
            return pres
        return None

    def med_name(self, med):
        if med.coding:
            name = next((coding.display for coding in med.coding if
                         coding.system == 'http://www.nlm.nih.gov/research/umls/rxnorm'), None)
            if name:
                return name
        if med.text and med.text:
            return med.text
        return "Unnamed Medication(TM)"

    def get_med_name(self, prescription, client=None):
        if prescription.medicationCodeableConcept is not None:
            med = prescription.medicationCodeableConcept
            return self.med_name(med)
        elif prescription.medicationReference is not None and client is not None:
            med = self.get_medication_by_ref(prescription.medicationReference.reference, client)
            return self.med_name(med)
        else:
            return 'Error: medication not found'
