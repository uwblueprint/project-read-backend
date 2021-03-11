from firebase_admin import credentials, initialize_app, auth
from rest_framework import authentication
from .exceptions import InvalidIDToken, ExpiredIDToken, MissingIDToken, RevokedIDToken, UserNotFound
from .models import User
import environ

env = environ.Env()

creds = {
    "type": "service_account",
    "project_id": env.str("FIREBASE_PROJECT_ID"),
    "project_key_id": env.str("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": env.str("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": env.str("FIREBASE_CLIENT_EMAIL"),
    "client_id": env.str("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": env.str("FiREBASE_CLIENT_CERT_URL"),
}

app = initialize_app(credentials.Certificate(creds))


class FirebaseAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION")
        if not auth_header:
            raise MissingIDToken

        id_token = auth_header.split(" ").pop()
        try:
            decoded_token = auth.verify_id_token(id_token)
        except auth.ExpiredIdTokenError:
            raise ExpiredIDToken
        except auth.RevokedIdTokenError:
            raise RevokedIDToken
        except auth.InvalidIdTokenError:
            raise InvalidIDToken

        if not id_token or not decoded_token:
            return None

        try:
            uid = decoded_token["uid"]
        except KeyError:
            raise InvalidIDToken

        try:
            user = User.objects.get(firebase_uid=uid)
        except User.DoesNotExist:
            raise UserNotFound
        return user, None

