from django.test.testcases import TestCase
from accounts.serializers import UserCreateSerializer
from unittest.mock import patch
from firebase_admin import auth
from rest_framework.serializers import ValidationError


class UserCreateSerializerTestCase(TestCase):
    def setUp(self):
        self.data = {"email": "test@asd.com"}

    @patch("accounts.models.User.objects.create")
    @patch("firebase_admin.auth.create_user")
    def test_user_create(self, mock_create, mock_model_create):
        uid = "test_uid"
        serializer = UserCreateSerializer(data=self.data)
        # anonymous object creation
        firebase_user = type("", (object,), {"uid": uid})()
        model_user = type("", (object,), {"firebase_uid": uid})()
        mock_create.return_value = firebase_user
        mock_model_create.return_value = model_user
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.firebase_uid, uid)
        mock_create.assert_called_once_with(email="test@asd.com")
        mock_model_create.assert_called_once()

    @patch("accounts.models.User.objects.create")
    @patch(
        "firebase_admin.auth.create_user",
        side_effect=auth.EmailAlreadyExistsError("message", "cause", "response"),
    )
    def test_user_create__firebase_user_exists(self, mock_create, mock_model_create):
        serializer = UserCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertRaises(ValidationError, serializer.save)
        mock_create.assert_called_once_with(email="test@asd.com")
        mock_model_create.assert_not_called()

    @patch("accounts.models.User.objects.create", side_effect=Exception(""))
    @patch("firebase_admin.auth.delete_user")
    @patch("firebase_admin.auth.create_user")
    def test_user_create__local_user_exists(
        self, mock_create, mock_delete, mock_model_create
    ):
        serializer = UserCreateSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())
        self.assertRaises(Exception, serializer.save)
        mock_create.assert_called_once()
        mock_delete.assert_called_once()
        mock_model_create.assert_called_once()
