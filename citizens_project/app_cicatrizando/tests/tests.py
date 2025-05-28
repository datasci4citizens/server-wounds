from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
from PIL import Image
import json
from datetime import datetime


from ..models import (
    Images, Patients, Specialists, TrackingRecords, 
    Wound, Comorbidities
)
from ..virtual_views import VirtualPatient
from ..omop.omop_models import Person

class APITests(TestCase):
    def setUp(self):
        """Configure test data and client for each test"""
        # Create test client
        self.client = APIClient()
        
        # Create test specialist
        self.specialist = Specialists.objects.create(
            specialist_name="Dr. Test",
            email="doctor@test.com",
            speciality="Dermatology"
        )
        
        User = get_user_model()

        self.test_user = User.objects.create_user(
            username='testuser', 
            password='testpassword'
        )       

        refresh = RefreshToken.for_user(self.test_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        # Create test patient
        self.patient = Patients.objects.create(
            name="Test Patient",
            email="patient@example.com",
            gender="Masculino",
            birthday=timezone.now(),
            specialist_id=self.specialist
        )
        
        # Create test comorbidity
        self.comorbidity = Comorbidities.objects.create(
            name="Diabetes"
        )
        
        # Create test wound
        self.wound = Wound.objects.create(
            patient_id=self.patient,
            specialist_id=self.specialist,
            region="Perna",
            type="Úlcera",
            start_date=timezone.now(),
            is_active=True
        )
    
    
    def test_list_patients(self):
        """Test getting list of patients"""
        url = reverse('patients-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Patient')
    
    def test_create_patient(self):
        """Test creating a new patient"""
        url = reverse('patients-list')
        data = {
            'name': 'New Patient',
            'email': 'new@example.com',
            'gender': 'Feminino',
            'birthday': '2000-01-01T00:00:00Z',
            'specialist_id': self.specialist.specialist_id
        }
        
        response = self.client.post(
            url, 
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patients.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Patient')


class OMOPMappingTests(TestCase):
    def setUp(self):
        self.specialist = Specialists.objects.create(
            specialist_name="OMOP Specialist",
            email="omop@test.com",
            speciality="Nursery"
        )
        self.patient = Patients.objects.create(
            name="OMOP Patient",
            email="omop_patient@example.com",
            gender="Masculino",
            birthday=timezone.now(),
            height=180,
            weight=80,
            smoke_frequency="1",
            drink_frequency="2",
            specialist_id=self.specialist,
            hospital_registration="HOSP123"
        )

    def test_patients_to_omop_person_mapping(self):
        """Test mapping from legacy Patients to OMOP Person"""
        # Create VirtualPatient instance from patient data
        patient_data = {
            'patient_id': self.patient.patient_id,
            'birthday': self.patient.birthday,
            'gender': self.patient.gender,
            'specialist_id': self.specialist.pk,
            'hospital_registration': self.patient.hospital_registration
        }
        vpatient = VirtualPatient()
        vpatient_obj = vpatient.descriptor().bindings['person_row'].model_from_data(**patient_data)
        # Check OMOP Person fields
        self.assertEqual(vpatient_obj['person_id'], self.patient.patient_id)
        self.assertEqual(vpatient_obj['birth_datetime'], self.patient.birthday)
        self.assertEqual(vpatient_obj['gender_concept_id'], self.patient.gender)
        self.assertEqual(vpatient_obj['provider_id'], self.specialist.pk)
        self.assertEqual(vpatient_obj['care_site_id'], self.patient.hospital_registration)

    def test_patients_to_omop_measurement_mapping(self):
        """Test mapping from Patients to OMOP Measurement"""
        patient_data = {
            'patient_id': self.patient.patient_id,
            'height': self.patient.height,
            'weight': self.patient.weight,
            'updated_at': self.patient.updated_at
        }
        vpatient = VirtualPatient()
        height_row = vpatient.descriptor().bindings['height_row'].model_from_data(**patient_data)
        weight_row = vpatient.descriptor().bindings['weight_row'].model_from_data(**patient_data)
        self.assertEqual(height_row['person_id'], self.patient.patient_id)
        self.assertEqual(height_row['value_as_number'], self.patient.height)
        self.assertEqual(weight_row['person_id'], self.patient.patient_id)
        self.assertEqual(weight_row['value_as_number'], self.patient.weight)

    def test_patients_to_omop_observation_mapping(self):
        """Test mapping from Patients to OMOP Observation"""
        patient_data = {
            'patient_id': self.patient.patient_id,
            'smoke_frequency': self.patient.smoke_frequency,
            'drink_frequency': self.patient.drink_frequency,
            'updated_at': self.patient.updated_at
        }
        vpatient = VirtualPatient()
        smoke_obs = vpatient.descriptor().bindings['smoke_frequency'].model_from_data(**patient_data)
        drink_obs = vpatient.descriptor().bindings['drink_frequency'].model_from_data(**patient_data)
        self.assertEqual(smoke_obs['person_id'], self.patient.patient_id)
        self.assertEqual(smoke_obs['value_as_concept_id'], self.patient.smoke_frequency)
        self.assertEqual(drink_obs['person_id'], self.patient.patient_id)
        self.assertEqual(drink_obs['value_as_concept_id'], self.patient.drink_frequency)

    def test_wound_to_omop_condition_occurrence_mapping(self):
        """Test mapping from Wound to OMOP ConditionOccurrence"""
        from ..virtual_views import VirtualWound
        wound_data = {
            'wound_id': 1,
            'patient_id': self.patient.patient_id,
            'specialist_id': self.specialist.pk,
            'start_date': timezone.now(),
            'end_date': None,
            'is_active': True
        }
        v_wound = VirtualWound()
        cond_row = v_wound.descriptor().bindings['condition_row'].model_from_data(**wound_data)
        self.assertEqual(cond_row['person_id'], self.patient.patient_id)
        self.assertEqual(cond_row['provider_id'], self.specialist.pk)
        self.assertEqual(cond_row['condition_occurrence_id'], 1)

    def test_wound_to_omop_note_mapping(self):
        """Test mapping from Wound to OMOP Note"""
        from ..virtual_views import VirtualWound
        wound_data = {
            'patient_id': self.patient.patient_id,
            'updated_at': timezone.now(),
            'image_id': 'img123',
            'wound_id': 1
        }
        v_wound = VirtualWound()
        note_row = v_wound.descriptor().bindings['note_row'].model_from_data(**wound_data)
        self.assertEqual(note_row['person_id'], self.patient.patient_id)
        self.assertEqual(note_row['note_text'], 'img123')
        self.assertEqual(note_row['note_event_id'], 1)