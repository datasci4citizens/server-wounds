"""
How to run this app test suite:

1) Run all tests via quickstart:
	python quickstart.py test

2) Run a specific test class:
	python quickstart.py test [Classname]

3) Run a specific test method:
	python quickstart.py test [Classname].[method_name]

Note:
- Run these commands from the server-wounds/ directory.
- for more information on commands, check server-wounds/quickstart.py docstring 
"""

from unittest.mock import patch
from datetime import date, datetime
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException
from app_cicatrizando.models import Provider, Patient, WoundsUser, Wound, Observation, WoundEtiology, WoundLocation
import io
from PIL import Image

class BaseTestClass(APITestCase):

	#auth urls
	google_login_url = "/auth/google/"
	specialist_registration_url = "/auth/register/specialist/"
	me_url = "/auth/me/"

	#features urls



	def _create_user_with_wounds_profile(self, *, email, role=None, full_name="", birth_date=None):
		first_name, _, last_name = full_name.strip().partition(" ") if full_name else ("", "", "")
		user = get_user_model().objects.create_user(
			username=email,
			email=email,
			first_name=first_name,
			last_name=last_name,
		)
		wounds_user = WoundsUser.objects.create(
			user=user,
			birth_date=birth_date,
			state="",
			city="",
			role=role or "",
		)
		return user, wounds_user
	
	def _create_Provider_or_Patient(self, *, WoundsUser: WoundsUser, role: str, **fields):
		if role not in ("patient", "provider"):
			raise ValueError("role needs to be an exact match with: 'patient' or 'provider'")
		
		if role == 'patient':

			patient = Patient.objects.create(


			)
			patient.wounds_user = WoundsUser

		if role == 'provider':
			provider = Provider.objects.create(
				wounds_user = WoundsUser


			)
		return provider or patient



	def _auth_headers(self, access_token):
		return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}

# Authentication Tests
class AuthenticationErrorTests(BaseTestClass):
	def test_me_requires_authentication(self):
		response = self.client.get(self.me_url)

		self.assertEqual(response.status_code, 401)

	def test_specialist_registration_requires_authentication(self):
		response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Test User",
				"birth_date": "1990-01-01",
				"state": "SP",
				"city": "São Paulo",
				"professional_id": "COREN-SP 12345",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 401)

	def test_google_login_requires_auth_code(self):
		response = self.client.post(
			self.google_login_url,
			{},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("auth_code", response.data)

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_fails_when_email_is_missing(self, mock_google_get_user_data):
		mock_google_get_user_data.side_effect = APIException("Google account does not have an email address")

		response = self.client.post(
			self.google_login_url,
			{"auth_code": "code-without-email"},
			format="json",
		)

		self.assertEqual(response.status_code, 500)

	def test_specialist_registration_requires_professional_id(self):
		user, wounds_user = self._create_user_with_wounds_profile(
			email="provider.missing.id@example.com",
		)

		self.client.force_authenticate(user=user)
		response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Test User",
				"birth_date": "1990-01-01",
				"state": "SP",
				"city": "São Paulo",
				# Missing professional_id
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("professional_id", response.data)
		self.assertFalse(Provider.objects.filter(wounds_user=wounds_user).exists())

	def test_specialist_registration_validates_brazilian_state(self):
		user, _ = self._create_user_with_wounds_profile(
			email="invalid.state@example.com",
		)

		self.client.force_authenticate(user=user)
		response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Test User",
				"birth_date": "1990-01-01",
				"state": "XX",  # Invalid state
				"city": "São Paulo",
				"professional_id": "COREN-SP 12345",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 400)
		self.assertIn("state", response.data)


class AuthenticationFlowTests(BaseTestClass):
	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_creates_new_user_returns_201(self, mock_google_get_user_data):
		mock_google_get_user_data.return_value = {
			"email": "new.user@example.com",
			"given_name": "New",
			"family_name": "User",
			"sub": "google-sub-new-001",
		}

		response = self.client.post(
			self.google_login_url,
			{"auth_code": "google-auth-code-new"},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["full_name"], "New User")
		self.assertEqual(response.data["email"], "new.user@example.com")
		self.assertIsNone(response.data["role"])
		self.assertFalse(response.data["registration_complete"])
		self.assertIn("access", response.data)
		self.assertIn("refresh", response.data)

		# Verify user was created
		user = get_user_model().objects.get(email="new.user@example.com")
		self.assertTrue(WoundsUser.objects.filter(user=user).exists())

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_google_login_existing_user_returns_200(self, mock_google_get_user_data):
		# Create existing user with complete registration
		user, wounds_user = self._create_user_with_wounds_profile(
			email="existing.user@example.com",
			full_name="Existing User",
			role=WoundsUser.Provider,
			birth_date=date(1990, 1, 1),
		)
		Provider.objects.create(
			wounds_user=wounds_user,
			professional_id="COREN-SP 12345",
		)

		mock_google_get_user_data.return_value = {
			"email": "existing.user@example.com",
			"given_name": "Existing",
			"family_name": "User",
			"sub": "google-sub-existing-001",
		}

		response = self.client.post(
			self.google_login_url,
			{"auth_code": "google-auth-code-existing"},
			format="json",
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["role"], "specialist")
		self.assertTrue(response.data["registration_complete"])

	@patch("app_cicatrizando.views.google_get_user_data")
	def test_full_specialist_registration_flow(self, mock_google_get_user_data):
		# Step 1: Google login (new user)
		mock_google_get_user_data.return_value = {
			"email": "new.specialist@example.com",
			"name": "Dr. João Silva",
			"sub": "google-sub-specialist-001",
		}

		login_response = self.client.post(
			self.google_login_url,
			{"auth_code": "google-auth-code-specialist"},
			format="json",
		)

		self.assertEqual(login_response.status_code, 201)
		self.assertFalse(login_response.data["registration_complete"])
		access_token = login_response.data["access"]

		# Step 2: Complete specialist registration
		registration_response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Dr. João Silva",
				"birth_date": "1985-03-15",
				"state": "SP",
				"city": "São Paulo",
				"professional_id": "COREN-SP 123456",
				"contact_phone": "11999998888",
				"contact_email": "joao.silva@hospital.com",
			},
			format="json",
			**self._auth_headers(access_token),
		)

		self.assertEqual(registration_response.status_code, 201)
		self.assertEqual(registration_response.data["message"], "Specialist registered successfully")
		self.assertEqual(registration_response.data["user"]["name"], "Dr. João Silva")
		self.assertEqual(registration_response.data["user"]["state"], "SP")
		self.assertEqual(registration_response.data["user"]["role"], "specialist")
		self.assertEqual(registration_response.data["specialist"]["professional_id"], "COREN-SP 123456")

		# Step 3: Verify /me endpoint
		me_response = self.client.get(
			self.me_url,
			**self._auth_headers(access_token),
		)

		self.assertEqual(me_response.status_code, 200)
		self.assertEqual(me_response.data["email"], "new.specialist@example.com")
		self.assertEqual(me_response.data["name"], "Dr. João Silva")
		self.assertEqual(me_response.data["role"], "specialist")
		self.assertTrue(me_response.data["registration_complete"])
		self.assertIsNotNone(me_response.data["specialist"])
		self.assertEqual(me_response.data["specialist"]["professional_id"], "COREN-SP 123456")

	def test_me_endpoint_incomplete_registration(self):
		user, _ = self._create_user_with_wounds_profile(
			email="incomplete@example.com",
		)

		self.client.force_authenticate(user=user)
		response = self.client.get(self.me_url)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data["email"], "incomplete@example.com")
		self.assertIsNone(response.data["role"])
		self.assertFalse(response.data["registration_complete"])
		self.assertIsNone(response.data.get("specialist"))

	def test_specialist_registration_updates_existing_wounds_user(self):
		user, wounds_user = self._create_user_with_wounds_profile(
			email="update.specialist@example.com",
		)

		self.client.force_authenticate(user=user)
		response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Updated Name",
				"birth_date": "1990-06-20",
				"state": "RJ",
				"city": "Rio de Janeiro",
				"professional_id": "COREN-RJ 654321",
				"contact_phone": "21988887777",
				"contact_email": "updated@hospital.com",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)

		# Verify WoundsUser was updated
		wounds_user.refresh_from_db()
		user.refresh_from_db()
		self.assertEqual(user.get_full_name(), "Updated Name")
		self.assertEqual(wounds_user.state, "RJ")
		self.assertEqual(wounds_user.city, "Rio de Janeiro")
		self.assertEqual(wounds_user.role, WoundsUser.Provider)

		# Verify Provider was created
		provider = Provider.objects.get(wounds_user=wounds_user)
		self.assertEqual(provider.professional_id, "COREN-RJ 654321")
		self.assertEqual(provider.contact_phone, "21988887777")
		self.assertEqual(provider.contact_email, "updated@hospital.com")

	def test_specialist_registration_state_is_uppercased(self):
		user, _ = self._create_user_with_wounds_profile(
			email="lowercase.state@example.com",
		)

		self.client.force_authenticate(user=user)
		response = self.client.post(
			self.specialist_registration_url,
			{
				"name": "Test User",
				"birth_date": "1990-01-01",
				"state": "sp",  # lowercase
				"city": "São Paulo",
				"professional_id": "COREN-SP 12345",
			},
			format="json",
		)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data["user"]["state"], "SP")  # Should be uppercased

# Features Tests

class ProviderFeaturesTests(BaseTestClass):

	patientlisturl = "specialist/patients"

	def setUp(self):
		super().setUp()
		# Use the proper instance method to create a user and assign to self
		self.user, self.woundsuser = self._create_user_with_wounds_profile(
			email="provider@example.com",
			role="Pr"
		)

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

    def test_specialist_can_upload_image_with_observation(self):
        self.client.force_authenticate(user=self.specialist_user)
        
        # 1. Create Wound
        wound = Wound.objects.create(
            patient=self.patient,
            etiology=WoundEtiology.DIABETIC_FOOT,
            location=WoundLocation.HALLUX
        )
        
        # 2. Create Dummy Image
        file_io = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(file_io, 'JPEG')
        file_io.seek(0)
        file_io.name = 'test_wound.jpg'

        # 3. Upload Observation with Image
        obs_url = f'{self.wounds_url}{wound.id}/observations/'
        obs_data = {
            "pain_level": 5,
            "exudate_amount": "Médio",
            "exudate_type": "Seroso",
            "tissue_type": "Granulação",
            "dressing_changes": 1,
            "periwound_skin": "Inchaço/Edema",
            "wound_edge": "Bem definidas, não aderidas à base da ferida",
            "fever_24h": False,
            "image": file_io
        }
        
        # We must use format='multipart' for file uploads
        response = self.client.post(obs_url, obs_data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image', response.data)
        self.assertIsNotNone(response.data['image'])
        # Verification of the URL (it should point to our S3/SeaweedFS endpoint)
        self.assertIn('wounds/observations/test_wound', response.data['image'])
