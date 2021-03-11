from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from firebase_admin import auth
from accounts.authentication import FirebaseAuthentication
from accounts.exceptions import InvalidIDToken, ExpiredIDToken, MissingIDToken, RevokedIDToken, UserNotFound
from unittest.mock import Mock, patch


class AuthenticationTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create(email="user@pr.com", firebase_uid="token")
        self.client.credentials(HTTP_AUTHORIZATION='auth_header')

    # def test_authenticated(self):
    #     auth.verify_id_token = Mock(return_value={"uid": "token"})
    #     response = self.client.get('/')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    # @patch('firebase_admin.auth.verify_id_token')
    # def test_expired_token(self, mock_verify):
    #     def mock_error():
    #         raise auth.ExpiredIdTokenError
    #     mock_verify.side_effect = mock_error
    #     self.assertRaises(ExpiredIDToken, self.client.get, '/')

    # def test_revoked_token(self):
    #     auth.verify_id_token = Mock(side_effect=auth.RevokedIdTokenError)
    #     self.assertRaises(RevokedIDToken, self.client.login, self.user)
    #
    @patch('firebase_admin.auth.verify_id_token')
    def test_invalid_token(self, mock_verify):
        mock_verify.side_effect = auth.InvalidIdTokenError
        print(self.client.get('/'))
        self.assertRaises(InvalidIDToken, self.client.get, '/')

    # def test_user_not_found(self):
    #     auth.verify_id_token = Mock(return_value={"uid": "some_other_token"})
    #     self.assertTrue(self.client.login(self.user))
