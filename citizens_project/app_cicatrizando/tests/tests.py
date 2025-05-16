from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
import tempfile
from PIL import Image
import json
from datetime import datetime
import tempfile

from ..models import (
    Images, Patients, Specialists, TrackingRecords, 
    Wound, Comorbidities
)

TEMP_MEDIA_ROOT = tempfile.mkdtemp()

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
    
    def get_temp_image(self):
        """Create a temporary image for testing"""
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        img = Image.new('RGB', (100, 100), color='red')
        img.save(temp_file, 'jpeg')
        temp_file.seek(0)
        return temp_file
    
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
        'birthday': '2000-01-01',
        'specialist_id': self.specialist.specialist_id,
        'height': 170,
        'weight': 70,
        'smoke_frequency': 'Não fumante',
        'drink_frequency': 'Social',
        'phone_number': '19999999999',
        'accept_tcl': True,
        'hospital_registration': '12345',
        'created_at': timezone.now().isoformat(),
        'comorbidities': [self.comorbidity.comorbidity_id]
        }
        
        response = self.client.post(
            url,
            data=data,
            format='json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Patients.objects.count(), 2)
        self.assertEqual(response.data['name'], 'New Patient')

    def test_get_patient_detail(self):
        """Test getting details of a specific patient"""
        url = reverse('patients-detail', args=[self.patient.patient_id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Patient')
    
    def test_update_patient(self):
        """Test updating patient details"""
        url = reverse('patients-detail', args=[self.patient.patient_id])
        data = {
            'name': 'Updated Patient Name',
            'email': self.patient.email,
            'gender': self.patient.gender,
            'birthday': self.patient.birthday.isoformat(),
            'specialist_id': self.specialist.specialist_id,
            'height': 175,
            'weight': 70,
            'smoke_frequency': 'Não fumante',
            'drink_frequency': 'Social',
            'phone_number': '11999999999',
            'accept_tcl': True,
            'hospital_registration': '12345',
            'comorbidities': [self.comorbidity.comorbidity_id]
        }
        
        response = self.client.put(
            url, 
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patient.refresh_from_db()
        self.assertEqual(self.patient.name, 'Updated Patient Name')

    @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
    def test_create_wound_with_image(self):
        """Test creating a wound with an attached image"""
        temp_image = self.get_temp_image()
    
        # Criar formulário de imagem para upload
        image_data = {
            'image': temp_image
        }
        
        # Fazer upload da imagem
        image_url = reverse('images-list')
        image_response = self.client.post(image_url, image_data, format='multipart')

        # Verificar se a imagem foi criada
        self.assertEqual(image_response.status_code, status.HTTP_201_CREATED)
        
        # Obter o ID da imagem criada
        image_id = image_response.data['image_id']
        
        # Criar ferida com o ID da imagem
        wound_url = reverse('wound-list')
        wound_data = {
            'patient_id': self.patient.patient_id,
            'specialist_id': self.specialist.specialist_id,
            'region': 'Braço',
            'type': 'Queimadura',
            'start_date': timezone.now().isoformat(),
            'image_id': image_id
        }
        
        wound_response = self.client.post(
            wound_url,
            data=json.dumps(wound_data),
            content_type='application/json'
        )

        self.assertEqual(wound_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Wound.objects.count(), 2)

        wound = Wound.objects.get(region='Braço')
        self.assertIsNotNone(wound.image_id)
    
    def test_archive_wound(self):
        """Test archiving a wound"""
        url = reverse('wound-archive', args=[self.wound.wound_id])
        response = self.client.put(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.wound.refresh_from_db()
        self.assertFalse(self.wound.is_active)
    
    def test_create_tracking_record(self):
        """Test creating tracking record"""
        url = reverse('trackingrecords-list')
        
        data = {
            'wound_id': self.wound.wound_id,
            'specialist_id': self.specialist.specialist_id,
            'length': 5.2,
            'width': 3.1,
            'track_date': timezone.now().isoformat(),
            'exudate_amount': 'Moderado',
            'exudate_type': 'Seroso',
            'tissue_type': 'Granulação'
        }
        
        response = self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TrackingRecords.objects.count(), 1)
    
    def test_list_wounds_by_patient(self):
        """Test listing wounds by patient"""
        url = f"{reverse('wound-list')}?patient_id={self.patient.patient_id}"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['region'], 'Perna')
    
    def test_comorbidity_crud(self):
        """Test CRUD for comorbidities"""
        # List
        list_url = reverse('comorbidities-list')
        list_response = self.client.get(list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        
        # Create
        create_data = {'name': 'Hipertensão'}
        create_response = self.client.post(
            list_url,
            data=json.dumps(create_data),
            content_type='application/json'
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        # Get detail
        detail_url = reverse('comorbidities-detail', args=[create_response.data['comorbidity_id']])
        detail_response = self.client.get(detail_url)
        self.assertEqual(detail_response.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_response.data['name'], 'Hipertensão')
        
        # Update
        update_data = {'name': 'Hipertensão Arterial'}
        update_response = self.client.put(
            detail_url,
            data=json.dumps(update_data),
            content_type='application/json'
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['name'], 'Hipertensão Arterial')
        
        # Delete
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)