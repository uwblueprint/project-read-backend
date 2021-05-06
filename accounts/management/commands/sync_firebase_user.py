import environ
from django.core.management.base import BaseCommand
import requests

from accounts.models import User

env = environ.Env()

FIREBASE_VERIFY_PASSWORD_URL = (
    "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword"
)


class Command(BaseCommand):
    help = "Syncs a Firebase user with a Django user"

    def add_arguments(self, parser):
        parser.add_argument(
            "email",
            type=str,
            nargs=1,
            help="Firebase & Django account email",
        )
        parser.add_argument(
            "password",
            type=str,
            nargs=1,
            help="Firebase account password",
        )

    def handle(self, *args, **options):
        email = options.get("email")[0]
        password = options.get("password")[0]

        json = requests.post(
            f"{FIREBASE_VERIFY_PASSWORD_URL}?key={env.str('FIREBASE_WEB_API_KEY')}",
            data={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
        ).json()

        firebase_uid = json["localId"]
        token = json["idToken"]

        user = User.objects.get(email=email)
        user.firebase_uid = firebase_uid
        user.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully synced user {email} with Firebase UID {firebase_uid}"
            ),
        )
        self.stdout.write(self.style.SUCCESS(f"Token (expires in 1 hour): {token}"))
