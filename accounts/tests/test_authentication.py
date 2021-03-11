from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework import status
from accounts.models import User
from firebase_admin import auth
from accounts.authentication import FirebaseAuthentication
from accounts.exceptions import InvalidIDToken, ExpiredIDToken, MissingIDToken, RevokedIDToken, UserNotFound
from unittest.mock import patch


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.client.credentials(HTTP_AUTHORIZATION='auth_header')
        self.user = User.objects.create(email="user@pr.com", firebase_uid="my_uid")
        self.factory = APIRequestFactory()
        self.request = self.factory.get('/', HTTP_AUTHORIZATION='auth_header')
        self.firebase = FirebaseAuthentication()

    def test_missing_token(self):
        request = self.factory.get('/')
        self.assertRaises(MissingIDToken, self.firebase.authenticate, request)
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('firebase_admin.auth.verify_id_token')
    def test_authenticated(self, mock_verify):
        mock_verify.return_value = {"uid": "my_uid"}
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @patch('firebase_admin.auth.verify_id_token')
    def test_expired_token(self, mock_verify):
        mock_verify.side_effect = auth.ExpiredIdTokenError('expired token', cause='expired')
        self.assertRaises(ExpiredIDToken, self.firebase.authenticate, self.request)
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('firebase_admin.auth.verify_id_token')
    def test_revoked_token(self, mock_verify):
        mock_verify.side_effect = auth.RevokedIdTokenError('revoked token')
        self.assertRaises(RevokedIDToken, self.firebase.authenticate, self.request)
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('firebase_admin.auth.verify_id_token')
    def test_invalid_token(self, mock_verify):
        mock_verify.side_effect = auth.InvalidIdTokenError('invalid token')
        self.assertRaises(InvalidIDToken, self.firebase.authenticate, self.request)
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @patch('firebase_admin.auth.verify_id_token')
    def test_user_not_found(self, mock_verify):
        mock_verify.return_value = {"uid": "some_other_uid"}
        self.assertRaises(UserNotFound, self.firebase.authenticate, self.request)
        response = self.client.get('/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

