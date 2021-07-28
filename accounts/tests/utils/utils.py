from accounts.models import User


def create_staff_user():
    return User.objects.create(
        email="user@test.com",
        first_name="Test",
        last_name="User",
    )
