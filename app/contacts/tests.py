from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import User, SpamNumber, Contact
from rest_framework_simplejwt.tokens import RefreshToken


class UserRegistrationTests(TestCase):
    def setUp(self):
        """Setup the API client for testing."""
        self.client = APIClient()

    def test_register_user(self):
        """Test user registration endpoint."""
        url = '/api/register/'
        data = {
            "username": "john",
            "phone_number": "1234567890",
            "password": "password@123",
            "email": "john@example.com"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully!')

    def test_register_user_without_email(self):
        """Test user registration endpoint."""
        url = '/api/register/'
        data = {
            "username": "john",
            "phone_number": "1234567890",
            "password": "password@123"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully!')

    def test_register_user_duplicate(self):
        """Test registration with duplicate username or phone number."""
        # Create a user first to make the username duplicate
        User.objects.create_user(
            username="user",
            password="password@123",
            email="user@example.com",
            phone_number="9876543210"
        )

        url = '/api/register/'
        data = {
            "username": "user",  # Duplicate username
            "phone_number": "9876543210",  # Duplicate phone number
            "password": "password@123",
            "email": "duplicate@example.com"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)  # Assuming unique username validation

    def test_register_user_invalid_email(self):
        """Test registration with invalid email format."""
        url = '/api/register/'
        data = {
            "username": "valid_user",
            "phone_number": "9876543210",
            "password": "password@123",
            "email": "invalidemail"
        }

        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)  # Invalid email error

    def test_register_user_invalid_phone(self):
        """Test registration with invalid email format."""
        url = '/api/register/'
        data = {
            "username": "valid_user",
            "phone_number": "98765432100000000",
            "password": "password@123",
        }

        response = self.client.post(url, data, format='json')

        # Assert that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Assert that the response contains the correct error message for the phone number
        self.assertIn('phone_number', response.data)
        self.assertEqual(
            response.data['phone_number'][0], "Enter a valid phone number with country code (e.g., +1234567890)."
        )


class UserProfileTests(TestCase):
    def setUp(self):
        """Setup user and API client for testing."""
        self.client = APIClient()

        # Creating a test user
        self.user = User.objects.create_user(
            username="test_user",
            phone_number="9876543210",
            password="password@123",
            email="test_user@example.com"
        )

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_profile(self):
        """Test getting user profile (authenticated)."""
        url = '/api/profile/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)

    def test_update_profile(self):
        """Test updating user profile (authenticated)."""
        url = '/api/profile/'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        data = {
            "email": "new_email@example.com"
        }

        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()  # Reload user from DB
        self.assertEqual(self.user.email, "new_email@example.com")

    def test_get_profile_unauthenticated(self):
        """Test accessing profile without authentication (should return 401)."""
        url = '/api/profile/'

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MarkSpamViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a test user
        self.user = User.objects.create_user(
            username="user",
            phone_number="1234567891",
            password="password@123",
            email="user@example.com"
        )

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

    def test_mark_spam_authenticated(self):
        """Test marking a phone number as spam with authentication."""
        # Set authentication header with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Mark a phone number as spam
        data = {"phone_number": "1234567890"}
        response = self.client.post("/api/mark_spam/", data, format="json")

        # Check that the response is successful
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the phone number has been marked as spam in the database
        spam_entry = SpamNumber.objects.get(phone_number="1234567890")
        self.assertEqual(spam_entry.phone_number, "1234567890")
        self.assertEqual(spam_entry.marked_by, self.user)
        self.assertEqual(spam_entry.marked_count, 1)
        self.assertEqual(spam_entry.spam_likelihood, 0.1)  # Assuming initial likelihood is 0.1

    def test_mark_spam_unauthenticated(self):
        """Test marking a phone number as spam without authentication."""
        # Make the same request without authentication
        data = {"phone_number": "1234567890"}
        response = self.client.post("/api/mark_spam/", data, format="json")

        # Check that the response is unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_mark_spam_phone_already_marked(self):
        """Test marking a phone number that is already marked as spam."""
        # Set authentication header with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Mark a phone number as spam
        phone_number = "1234567890"
        SpamNumber.objects.create(
            phone_number=phone_number,
            marked_by=self.user,
            marked_count=1,
            spam_likelihood=0.1
        )

        # Try marking the same phone number again
        data = {"phone_number": phone_number}
        response = self.client.post("/api/mark_spam/", data, format="json")

        # Check that the response is successful (status code 200 or 204)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure the marked_count is incremented
        spam_entry = SpamNumber.objects.get(phone_number=phone_number)
        self.assertEqual(spam_entry.marked_count, 2)

    def test_mark_spam_invalid_phone_number(self):
        """Test marking an invalid phone number."""
        # Set authentication header with the token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Invalid phone number
        data = {"phone_number": "invalid_number"}
        response = self.client.post("/api/mark_spam/", data, format="json")

        # Check that the response is a bad request (status code 400)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('phone_number', response.data)


class SearchPersonViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Creating a test user
        self.user = User.objects.create_user(
            username="user",
            phone_number="1234567891",
            password="password@123",
            email="user@example.com"
        )

        # Generate JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        self.refresh_token = str(refresh)

        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Creating some Contact instances
        self.contact_1 = Contact.objects.create(name="John Doe", phone_number="1234567890", user=self.user)
        self.contact_2 = Contact.objects.create(name="Jane john Smith", phone_number="9876543210", user=self.user)
        self.contact_3 = Contact.objects.create(name="Jack Black", phone_number="5551234567", user=self.user)
        self.contact_3 = Contact.objects.create(name="5551234567", phone_number="5551234567", user=self.user)

        # Creating SpamNumber instances
        self.spam_1 = SpamNumber.objects.create(
            phone_number="1234567890",
            marked_by=self.user,
            marked_count=5,
            spam_likelihood=0.8
        )
        self.spam_2 = SpamNumber.objects.create(
            phone_number="9876543210",
            marked_by=self.user,
            marked_count=2,
            spam_likelihood=0.4
        )

    def test_search_by_name(self):
        """Test searching by name."""
        url = '/api/search/'
        data = {'query': 'John'}
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[1]['name'], 'Jane john Smith')

    def test_search_by_phone_number(self):
        """Test searching by phone number."""
        url = '/api/search/'
        data = {'query': '9876543210'}
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['phone_number'], '9876543210')

    def test_search_by_name_and_phone_number(self):
        """Test searching by both name and phone number."""
        url = '/api/search/'
        data = {'query': '5551234567'}
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

        self.assertEqual(response.data[0]['phone_number'], '5551234567')
        self.assertEqual(response.data[0]['name'], '5551234567')
        self.assertEqual(response.data[1]['phone_number'], '5551234567')
        self.assertEqual(response.data[1]['name'], 'Jack Black')

    #
    def test_search_with_spam_likelihood(self):
        """Test that spam likelihood is included in search results."""
        url = '/api/search/'
        data = {'query': 'John'}
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'John Doe')
        self.assertEqual(response.data[0]['spam_likelihood'], 0.8)
        self.assertEqual(response.data[1]['name'], 'Jane john Smith')
        self.assertEqual(response.data[1]['spam_likelihood'], 0.4)

    def test_search_no_results(self):
        """Test that no results are returned for an invalid search."""
        url = '/api/search/'
        data = {'query': 'Nonexistent Name'}
        response = self.client.get(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)  # No results should be returned
