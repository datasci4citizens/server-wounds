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
from datetime import date
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework.exceptions import APIException
from app_cicatrizando.models import Provider, Patient, WoundsUser


class BaseAuthenticationFlowTests(APITestCase):
	google_login_url = "/auth/google/"
	specialist_registration_url = "/auth/register/specialist/"
	me_url = "/auth/me/"

	def _create_user_with_wounds_profile(self, *, email, role=None, name="", birth_date=None):
		user = get_user_model().objects.create_user(username=email, email=email)
		wounds_user = WoundsUser.objects.create(
			user=user,
			name=name,
			birth_date=birth_date,
			state="",
			city="",
			role=role or "",
		)
		return user, wounds_user

	def _auth_headers(self, access_token):
		return {"HTTP_AUTHORIZATION": f"Bearer {access_token}"}


class AuthenticationErrorTests(BaseAuthenticationFlowTests):
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
		user, _ = self._create_user_with_wounds_profile(
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
		self.assertFalse(Provider.objects.filter(wounds_user=user).exists())

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


class AuthenticationFlowTests(BaseAuthenticationFlowTests):
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
			name="Existing User",
			role=WoundsUser.Provider,
			birth_date=date(1990, 1, 1),
		)
		Provider.objects.create(
			wounds_user=user,
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
		self.assertIsNone(response.data["specialist"])

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
		self.assertEqual(wounds_user.name, "Updated Name")
		self.assertEqual(wounds_user.state, "RJ")
		self.assertEqual(wounds_user.city, "Rio de Janeiro")
		self.assertEqual(wounds_user.role, WoundsUser.Provider)

		# Verify Provider was created
		provider = Provider.objects.get(wounds_user=user)
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
