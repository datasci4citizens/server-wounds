from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from app_cicatrizando.models import WoundsUser, Provider, Patient, Wound, Observation, WoundEtiology, WoundLocation
from datetime import date

User = get_user_model()

class WoundMVPTests(APITestCase):
    def setUp(self):
        # Create a specialist
        self.specialist_user = User.objects.create_user(username='specialist@example.com', email='specialist@example.com', first_name='Dr.', last_name='Specialist')
        self.specialist_wounds_user = WoundsUser.objects.create(user=self.specialist_user, role=WoundsUser.Provider, state='SP', city='São Paulo')
        self.provider = Provider.objects.create(wounds_user=self.specialist_wounds_user, professional_id='COREN-SP 12345')

        # Create a patient
        self.patient_user = User.objects.create_user(username='patient@example.com', email='patient@example.com', first_name='John', last_name='Doe')
        self.patient_wounds_user = WoundsUser.objects.create(user=self.patient_user, role=WoundsUser.Patient, state='SP', city='São Paulo')
        self.patient = Patient.objects.create(wounds_user=self.patient_wounds_user)
        self.patient.assigned_providers.add(self.provider)

        # URLs
        self.wounds_url = '/wounds/'

    def test_specialist_can_create_wound_and_observation(self):
        self.client.force_authenticate(user=self.specialist_user)
        
        # 1. Create Wound
        wound_data = {
            "patient": self.patient.id,
            "etiology": WoundEtiology.DIABETIC_FOOT,
            "location": WoundLocation.HALLUX
        }
        response = self.client.post(self.wounds_url, wound_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        wound_id = response.data['id']
        
        # 2. Create Observation
        obs_url = f'{self.wounds_url}{wound_id}/observations/'
        obs_data = {
            "pain_level": 5,
            "exudate_amount": "Médio",
            "exudate_type": "Seroso",
            "tissue_type": "Granulação",
            "dressing_changes": 1,
            "periwound_skin": "Inchaço/Edema",
            "wound_edge": "Bem definidas, não aderidas à base da ferida",
            "fever_24h": False,
            "extra_notes": "Specialist confidential note",
            "patient_guidelines": "Keep it clean"
        }
        response = self.client.post(obs_url, obs_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['extra_notes'], "Specialist confidential note")

    def test_patient_access_and_privacy(self):
        # Create a wound and observation first
        wound = Wound.objects.create(
            patient=self.patient,
            etiology=WoundEtiology.PRESSURE_INJURY,
            location=WoundLocation.CALCANEAL
        )
        obs = Observation.objects.create(
            wound=wound,
            author=self.specialist_wounds_user,
            pain_level=3,
            exudate_amount="Pouco",
            exudate_type="Seroso",
            tissue_type="Epitelização",
            dressing_changes=1,
            periwound_skin="Eritema menor que 2 cm",
            wound_edge="Definidas, contorno claramente visível, aderidas, niveladas com a base da ferida",
            fever_24h=False,
            extra_notes="Specialist secret note",
            patient_guidelines="Guideline for patient"
        )

        self.client.force_authenticate(user=self.patient_user)
        
        # 1. Patient should see their wound
        response = self.client.get(self.wounds_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], wound.id)

        # 2. Patient should see observations but NOT extra_notes from specialist
        obs_url = f'{self.wounds_url}{wound.id}/observations/'
        response = self.client.get(obs_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertIsNone(response.data[0]['extra_notes'])
        self.assertEqual(response.data[0]['patient_guidelines'], "Guideline for patient")

    def test_patient_cannot_create_wound(self):
        self.client.force_authenticate(user=self.patient_user)
        wound_data = {
            "patient": self.patient.id,
            "etiology": WoundEtiology.DIABETIC_FOOT,
            "location": WoundLocation.HALLUX
        }
        response = self.client.post(self.wounds_url, wound_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_specialist_only_sees_assigned_patients_wounds(self):
        # Create another patient NOT assigned to this specialist
        other_user = User.objects.create_user(username='other@example.com', email='other@example.com')
        other_wounds_user = WoundsUser.objects.create(user=other_user, role=WoundsUser.Patient)
        other_patient = Patient.objects.create(wounds_user=other_wounds_user)
        
        Wound.objects.create(
            patient=other_patient,
            etiology=WoundEtiology.SURGICAL,
            location=WoundLocation.KNEE_ANTERIOR
        )

        self.client.force_authenticate(user=self.specialist_user)
        response = self.client.get(self.wounds_url)
        # Should only see John Doe's wound (none created yet in this test for John Doe, so 0)
        self.assertEqual(len(response.data), 0)
