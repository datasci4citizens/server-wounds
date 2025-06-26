from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
import tempfile
from PIL import Image as PILImage
import io
import json
from datetime import datetime
import base64
import os

from ..virtual_models import (
    VirtualPatient, VirtualWound, VirtualTrackingRecords, 
    VirtualComorbidity, VirtualSpecialist
)
from ..virtual_views import (
    VirtualPatientViewSet, VirtualWoundViewSet, VirtualTrackingRecordsViewSet,
    VirtualComorbidityViewSet, VirtualSpecialistViewSet
)

from ..models import Image as ImageModel, TrackingRecordImage, WoundImage, PatientNonClinicalInfos
from ..omop.omop_models import Concept, Person, Provider, Observation, Measurement, ConditionOccurrence, CareSite, Vocabulary, Domain, ConceptClass
from ..omop.omop_ids import (
    CID_SMOKE_FREQUENCY, CID_NEVER, CID_OCCASIONALLY, CID_10_OR_LESS, CID_10_OR_MORE,
    CID_DRINK_FREQUENCY, CID_DRINK_2_3_TIMES_WEEK, CID_DRINK_2_4_TIMES_MONTH, 
    CID_DRINK_4_OR_MORE_WEEK, CID_DRINK_MONTHLY_OR_LESS, CID_DRINK_NEVER,
    CID_EXUDATE_APPEARANCE, CID_EXUDATE_PURULENT, CID_EXUDATE_SANGUINOUS, 
    CID_EXUDATE_SEROPURULENT, CID_EXUDATE_SEROSANGUINOUS, CID_EXUDATE_SEROUS, CID_EXUDATE_VISCOUS,
    CID_WOUND_APPEARANCE, CID_WOUND_APPROXIMATED, CID_WOUND_CLOSED_RESURFACED, 
    CID_WOUND_EDGE_DESCRIPTION, CID_WOUND_EDGE_ATTACHED, CID_WOUND_EDGE_NOT_ATTACHED, 
    CID_WOUND_EDGE_POORLY_DEFINED, CID_WOUND_EDGE_ROLLED, CID_WOUND_EDGE_SCABBED, CID_WOUND_EDGE_WELL_DEFINED,
    CID_PAIN_SEVERITY, CID_PAIN_SCALE_TYPE,
    CID_WOUND_TYPE, CID_WOUND_ABRASION, CID_WOUND_AVULSION, CID_WOUND_BITE, CID_WOUND_BLISTER,
    CID_BURN, CID_WOUND_CONTUSION, CID_WOUND_CRUSH, CID_WOUND_ERYTHEMA, CID_WOUND_FISSURE,
    CID_WOUND_GRAFT, CID_WOUND_GUNSHOT, CID_WOUND_LACERATION, CID_WOUND_MACERATION, CID_WOUND_PRESSURE_ULCER,
    CID_WOUND_PUNCTURE, CID_WOUND_RASH, CID_SURGICAL_WOUND, CID_TRAUMATIC_WOUND, CID_WOUND_PRESSURE_ULCER,
    CID_REGION_ABDOMEN, CID_WOUND_LACERATION, CID_DIABETES
)

@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class BaseAPITestCase(APITestCase):
    """Base class for API tests providing common setup and utility functions"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up data for the entire test case"""
        # Create Concepts for each ConceptClass's concept_class_concept_id
        Concept.objects.create(
            concept_id=20001,
            concept_name="Test ConceptClass Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="TEST_CONCEPTCLASS",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        Concept.objects.create(
            concept_id=20002,
            concept_name="Domain ConceptClass Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Domain",
            standard_concept="S",
            concept_code="DOMAIN_CONCEPTCLASS",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        # Create required ConceptClass records for Concept foreign keys
        ConceptClass.objects.create(concept_class_id="Test", concept_class_name="Test Class", concept_class_concept_id=20001)
        ConceptClass.objects.create(concept_class_id="Domain", concept_class_name="Domain Class", concept_class_concept_id=20002)
        # Create Concepts for each Domain's domain_concept_id
        Concept.objects.create(
            concept_id=10001,
            concept_name="Race/Ethnicity Domain Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Domain",
            standard_concept="S",
            concept_code="RACE_ETHNICITY_DOMAIN",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        Concept.objects.create(
            concept_id=10002,
            concept_name="Gender Domain Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Domain",
            standard_concept="S",
            concept_code="GENDER_DOMAIN",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        Concept.objects.create(
            concept_id=10003,
            concept_name="Specialty Domain Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Domain",
            standard_concept="S",
            concept_code="SPECIALTY_DOMAIN",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        Concept.objects.create(
            concept_id=10004,
            concept_name="Test Domain Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Domain",
            standard_concept="S",
            concept_code="TEST_DOMAIN",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        # Create required Domain records for Concept foreign keys
        Domain.objects.create(domain_id="Race/Ethnicity", domain_name="Race/Ethnicity", domain_concept_id=10001)
        Domain.objects.create(domain_id="Gender", domain_name="Gender", domain_concept_id=10002)
        Domain.objects.create(domain_id="Specialty", domain_name="Specialty", domain_concept_id=10003)
        Domain.objects.create(domain_id="Test Domain", domain_name="Test Domain", domain_concept_id=10004)
        # Create a Concept for vocabulary_concept_id foreign key
        Concept.objects.create(
            concept_id=1,
            concept_name="Test Vocabulary Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="TEST_VOCAB_CONCEPT",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        # Now create the Vocabulary record
        Vocabulary.objects.create(
            vocabulary_id="Test",
            vocabulary_name="Test Vocabulary",
            vocabulary_reference="Test Reference",
            vocabulary_version="v1",
            vocabulary_concept_id=1
        )
        
        # Create test user model
        User = get_user_model()
        cls.username = 'testuser'
        cls.password = 'testpassword'
        cls.test_user = User.objects.create_user(
            username=cls.username, 
            password=cls.password,
            email='test@example.com',
            is_superuser=True,
            is_staff=True
        )
        
        Concept.objects.create(
        concept_id=4168335,
        concept_name="Wound Specialist",
        domain_id="Specialty",
        vocabulary_id="Test",
        concept_class_id="Test",
        standard_concept="S",
        concept_code="WOUND",
        valid_start_date=timezone.now(),
        valid_end_date=timezone.now(),
        invalid_reason=None
    )
        
        # Create test specialist using Provider model (OMOP)
        cls.provider = Provider.objects.create(
            provider_id=1000,
            provider_name="Dr. Test Specialist",
            specialty_concept_id=4168335  # Using CID_WOUND which is a valid concept ID
        )
        
        # Create test patient using Person model (OMOP)
        cls.person = Person.objects.create(
            person_id=1000,
            birth_datetime=timezone.now(),
            gender_concept_id=2222222,
            provider_id=cls.provider.provider_id,
            care_site_id=123123,
            year_of_birth=timezone.now().year,  # Add required field
            ethnicity_concept_id=0,  # Using CID_NULL
            race_concept_id=0  # Using CID_NULL
        )
        
        # Add missing Concept for observation_concept_id=2000000001
        Concept.objects.create(
            concept_id=2000000001,
            concept_name="Observation Concept",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="OBSERVATION",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )

        Concept.objects.create(
            concept_id=100001,
            concept_name="Diabetes",
            domain_id="Test Domain",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="DIABETES",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )
        # Create virtual patient data with valid string choices and required fields
        cls.patient_data = {
            'patient_id': cls.person.person_id,
            'name': "Test Patient",
            'gender': "male",
            'birthday': cls.person.birth_datetime.isoformat(),
            'specialist_id': cls.provider.provider_id,
            'hospital_registration': cls.person.care_site_id,
            'phone_number': "1234567890",
            'weight': 75.5,
            'height': 175.0,
            'accept_tcl': True,
            'smoke_frequency': CID_NEVER,
            'drink_frequency': CID_DRINK_NEVER,
            'comorbidities': [],
            'updated_at': timezone.now().isoformat()
        }
        cls.wound_data = {
            'wound_id': 1000,
            'patient_id': cls.person.person_id,
            'specialist_id': cls.provider.provider_id,
            'region': CID_REGION_ABDOMEN,
            'wound_type': CID_WOUND_PRESSURE_ULCER,
            'start_date': timezone.now().isoformat(),
            'is_active': True,
            'updated_at': timezone.now().isoformat(),
            'image_id': None
        }
        cls.tracking_data = {
            'tracking_id': 1000,
            'patient_id': cls.person.person_id,
            'specialist_id': cls.provider.provider_id,
            'wound_id': 1000,
            'track_date': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'length': 10.5,
            'width': 5.2,
            'exudate_amount': 1,
            'exudate_type': CID_EXUDATE_SEROSANGUINOUS,
            'tissue_type': CID_WOUND_APPROXIMATED,
            'wound_edges': CID_WOUND_EDGE_WELL_DEFINED,
            'skin_around': CID_EXUDATE_SEROUS,
            'had_a_fever': 0,
            'pain_level': 3,
            'dressing_changes_per_day': 2,
            'image_id': None,
            'guidelines_to_patient': 'Change dressing twice daily, keep the wound clean',
            'extra_notes': 'Patient reports less pain than last visit'
        }
        cls.comorbidity_data = {
            'patient_id': cls.person.person_id,
            'comorbidity_id': 1000,
            'specialist_id': cls.provider.provider_id,
            'comorbidity_type': CID_DIABETES,
            'start_date': timezone.now().isoformat(),
            'updated_at': timezone.now().isoformat(),
            'is_active': True
        }
        
        Concept.objects.create(
            concept_id=0,
            concept_name="Unknown",
            domain_id="Race/Ethnicity",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="UNKNOWN",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )

        Concept.objects.create(
            concept_id=2222222,
            concept_name="Unknown Gender",
            domain_id="Gender",
            vocabulary_id="Test",
            concept_class_id="Test",
            standard_concept="S",
            concept_code="UNKNOWN_GENDER",
            valid_start_date=timezone.now(),
            valid_end_date=timezone.now(),
            invalid_reason=None
        )

        CareSite.objects.create(
            care_site_id=123123,
            care_site_name="Test Care Site"
        )
        
        # Add Concepts for all test data concept IDs
        for cid, cname in [
            (CID_REGION_ABDOMEN, "Abdomen"),
            (CID_WOUND_PRESSURE_ULCER, "Pressure Ulcer"),
            (CID_WOUND_LACERATION, "Laceration"),
            (CID_EXUDATE_SEROSANGUINOUS, "Serosanguineous"),
            (CID_WOUND_APPROXIMATED, "Approximated"),
            (CID_WOUND_EDGE_WELL_DEFINED, "Well Defined"),
            (CID_EXUDATE_SEROUS, "Serous"),
            (CID_NEVER, "Never"),
            (CID_DRINK_NEVER, "Never Drink"),
            (CID_DIABETES, "Diabetes")
        ]:
            Concept.objects.get_or_create(
                concept_id=cid,
                defaults={
                    'concept_name': cname,
                    'domain_id': "Test Domain",
                    'vocabulary_id': "Test",
                    'concept_class_id': "Test",
                    'standard_concept': "S",
                    'concept_code': cname.upper().replace(" ", "_"),
                    'valid_start_date': timezone.now(),
                    'valid_end_date': timezone.now(),
                    'invalid_reason': None
                }
            )
        
    def setUp(self):
        """Set up for each test method"""
        self.client = APIClient()
        # Force authenticate user for all API calls
        self.client.force_authenticate(user=self.test_user)
        
    def _create_temp_image(self):
        """Create a temporary image file for testing"""
        image = PILImage.new('RGB', (100, 100), color='red')
        tmp_file = io.BytesIO()
        image.save(tmp_file, format='JPEG')
        tmp_file.seek(0)
        from django.core.files.uploadedfile import SimpleUploadedFile
        return SimpleUploadedFile("test.jpg", tmp_file.read(), content_type="image/jpeg")

    def assertResponseStatus(self, response, expected_status, msg=None):
        if response.status_code != expected_status:
            print(f"\nRequest to {getattr(response, 'request', {}).get('path', 'unknown')} failed.")
            print(f"Expected: {expected_status}, Got: {response.status_code}")
            print(f"Response data: {getattr(response, 'data', response.content)}\n")
        self.assertEqual(response.status_code, expected_status, msg)

class AuthenticationTest(BaseAPITestCase):
    """Tests for authentication endpoints"""
    
    def test_me_endpoint(self):
        """Test the me endpoint returns current user info"""
        url = '/auth/me/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.username)


class PatientAPITest(BaseAPITestCase):
    """Tests for patient API endpoints"""
    
    def test_list_patients(self):
        url = '/patients/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_patient(self):
        url = '/patients/'
        response = self.client.post(url, self.patient_data, format='json')
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['name'], self.patient_data['name'])

    def test_retrieve_patient(self):
        create_url = '/patients/'
        create_response = self.client.post(create_url, self.patient_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            patient_id = create_response.data['patient_id']
            url = f'/patients/{patient_id}/'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['name'], self.patient_data['name'])

    def test_update_patient(self):
        create_url = '/patients/'
        create_response = self.client.post(create_url, self.patient_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            patient_id = create_response.data['patient_id']
            updated_data = self.patient_data.copy()
            updated_data['name'] = "Updated Name"
            url = f'/patients/{patient_id}/'
            response = self.client.put(url, updated_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['name'], "Updated Name")


class WoundAPITest(BaseAPITestCase):
    """Tests for wound API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.client.post('/patients/', self.patient_data, format='json')
    
    def test_list_wounds(self):
        url = '/wounds/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_wound(self):
        url = '/wounds/'
        response = self.client.post(url, self.wound_data, format='json')
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['region'], self.wound_data['region'])
            self.assertEqual(response.data['wound_type'], self.wound_data['wound_type'])

    def test_retrieve_wound(self):
        create_url = '/wounds/'
        create_response = self.client.post(create_url, self.wound_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            wound_id = create_response.data['wound_id']
            url = f'/wounds/{wound_id}/'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['region'], self.wound_data['region'])

    def test_update_wound(self):
        create_url = '/wounds/'
        create_response = self.client.post(create_url, self.wound_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            wound_id = create_response.data['wound_id']
            updated_data = self.wound_data.copy()
            updated_data['region'] = "Braço"
            url = f'/wounds/{wound_id}/'
            response = self.client.put(url, updated_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['region'], "Braço")


class TrackingRecordAPITest(BaseAPITestCase):
    """Tests for tracking records API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.client.post('/patients/', self.patient_data, format='json')
        self.client.post('/wounds/', self.wound_data, format='json')
    
    def test_list_tracking_records(self):
        url = '/tracking-records/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_tracking_record(self):
        url = '/tracking-records/'
        response = self.client.post(url, self.tracking_data, format='json')
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['length'], self.tracking_data['length'])
            self.assertEqual(response.data['width'], self.tracking_data['width'])

    def test_retrieve_tracking_record(self):
        create_url = '/tracking-records/'
        create_response = self.client.post(create_url, self.tracking_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            tracking_id = create_response.data['tracking_id']
            url = f'/tracking-records/{tracking_id}/'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['length'], self.tracking_data['length'])

    def test_update_tracking_record(self):
        create_url = '/tracking-records/'
        create_response = self.client.post(create_url, self.tracking_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            tracking_id = create_response.data['tracking_id']
            updated_data = self.tracking_data.copy()
            updated_data['length'] = 12.7
            url = f'/tracking-records/{tracking_id}/'
            response = self.client.put(url, updated_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['length'], 12.7)


class ComorbidityAPITest(BaseAPITestCase):
    """Tests for comorbidity API endpoints"""
    
    def setUp(self):
        super().setUp()
        self.client.post('/patients/', self.patient_data, format='json')
    
    def test_list_comorbidities(self):
        url = '/comorbidities/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_create_comorbidity(self):
        url = '/comorbidities/'
        response = self.client.post(url, self.comorbidity_data, format='json')
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data['comorbidity_type'], self.comorbidity_data['comorbidity_type'])

    def test_retrieve_comorbidity(self):
        create_url = '/comorbidities/'
        create_response = self.client.post(create_url, self.comorbidity_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            comorbidity_id = create_response.data['comorbidity_id']
            url = f'/comorbidities/{comorbidity_id}/'
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['comorbidity_type'], self.comorbidity_data['comorbidity_type'])

    def test_update_comorbidity(self):
        create_url = '/comorbidities/'
        create_response = self.client.post(create_url, self.comorbidity_data, format='json')
        if create_response.status_code == status.HTTP_201_CREATED:
            comorbidity_id = create_response.data['comorbidity_id']
            updated_data = self.comorbidity_data.copy()
            updated_data['comorbidity_id'] = comorbidity_id
            updated_data['comorbidity_type'] = CID_DIABETES
            url = f'/comorbidities/{comorbidity_id}/'
            response = self.client.put(url, updated_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['comorbidity_type'], CID_DIABETES)


class ImageAPITest(BaseAPITestCase):
    """Tests for image upload and association with wounds and tracking records"""
    def setUp(self):
        super().setUp()
        self.client.post('/patients/', self.patient_data, format='json')
        self.wound_response = self.client.post('/wounds/', self.wound_data, format='json')
        self.tracking_response = self.client.post('/tracking-records/', self.tracking_data, format='json')

    def test_upload_image(self):
        url = '/images/'
        image = self._create_temp_image()
        response = self.client.post(url, {'image': image}, format='multipart')
        self.assertResponseStatus(response, status.HTTP_201_CREATED)
        if response.status_code == status.HTTP_201_CREATED:
            self.assertIn('image', response.data)
            image_url = response.data['image']
            # Optionally, check the file exists if needed

    def test_associate_image_with_wound(self):
        image_url = '/images/'
        image = self._create_temp_image()
        image_response = self.client.post(image_url, {'image': image}, format='multipart')
        if image_response.status_code == status.HTTP_201_CREATED:
            wound_image_url = '/wounds/image/'
            wound_id = self.wound_response.data.get('wound_id') if hasattr(self, 'wound_response') and self.wound_response.status_code == status.HTTP_201_CREATED else None
            image_id = image_response.data['id']
            if wound_id is not None:
                association_data = {
                    'wound_id': wound_id,
                    'image_id': image_id
                }
                response = self.client.post(wound_image_url, association_data, format='json')
                self.assertResponseStatus(response, status.HTTP_201_CREATED)
                image_model = ImageModel.objects.get(id=image_id)
                if image_model.image and os.path.exists(image_model.image.path):
                    os.remove(image_model.image.path)

    def test_associate_image_with_tracking_record(self):
        image_url = '/images/'
        image = self._create_temp_image()
        image_response = self.client.post(image_url, {'image': image}, format='multipart')
        if image_response.status_code == status.HTTP_201_CREATED:
            tracking_image_url = '/tracking-records/image/'
            tracking_id = self.tracking_response.data.get('tracking_id') if hasattr(self, 'tracking_response') and self.tracking_response.status_code == status.HTTP_201_CREATED else None
            image_id = image_response.data['id']
            if tracking_id is not None:
                association_data = {
                    'tracking_record_id': tracking_id,
                    'image_id': image_id
                }
                response = self.client.post(tracking_image_url, association_data, format='json')
                self.assertResponseStatus(response, status.HTTP_201_CREATED)
                image_model = ImageModel.objects.get(id=image_id)
                if image_model.image and os.path.exists(image_model.image.path):
                    os.remove(image_model.image.path)

class FilteringTest(BaseAPITestCase):
    """Tests for filtering capabilities in the API"""
    
    def setUp(self):
        super().setUp()
        self.client.post('/patients/', self.patient_data, format='json')
        self.client.post('/wounds/', self.wound_data, format='json')
        second_wound_data = self.wound_data.copy()
        second_wound_data['wound_id'] = 1001
        second_wound_data['wound_type'] = CID_WOUND_LACERATION
        self.client.post('/wounds/', second_wound_data, format='json')
    def test_filter_wounds_by_type(self):
        url = f"/wounds/?wound_type={CID_WOUND_PRESSURE_ULCER}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data[0]['wound_type'], CID_WOUND_PRESSURE_ULCER)
        response = self.client.get(f"/wounds/?wound_type={CID_WOUND_LACERATION}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.status_code == status.HTTP_200_OK:
            self.assertEqual(response.data[0]['wound_type'], CID_WOUND_LACERATION)

    def test_filter_wounds_by_patient(self):
        url = f"/wounds/?patient_id={self.person.person_id}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        if response.status_code == status.HTTP_200_OK:
            self.assertTrue(len(response.data) >= 2)