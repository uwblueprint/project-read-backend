from datetime import timezone
from django.test.testcases import TestCase

from accounts.models import User
from accounts.serializers import UserSerializer


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            email="peter@parker.com",
            first_name="Peter",
            is_active=True,
            is_admin=True,
            last_name="Parker",
        )

    def test_user_serializer(self):
        self.assertEqual(
            {
                "id": self.user.id,
                "date_joined": self.user.date_joined.replace(tzinfo=timezone.utc)
                .astimezone(tz=None)
                .isoformat(),
                "email": self.user.email,
                "first_name": self.user.first_name,
                "is_active": self.user.is_active,
                "is_admin": self.user.is_admin,
                "last_name": self.user.last_name,
            },
            UserSerializer(self.user, context={"request": None}).data,
        )
