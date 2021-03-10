from rest_framework import status
from rest_framework.exceptions import APIException


class MissingIDToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "No ID token provided"
    default_code = "token_missing"


class InvalidIDToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Invalid ID token provided"
    default_code = "invalid_token"


class ExpiredIDToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "ID token expired"
    default_code = "token_expired"


class RevokedIDToken(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "ID token revoked"
    default_code = "token_revoked"

