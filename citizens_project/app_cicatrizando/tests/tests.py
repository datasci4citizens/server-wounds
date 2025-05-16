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