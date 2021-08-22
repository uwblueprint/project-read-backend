from .base import *

ALLOWED_HOSTS = ["project-read-backend.herokuapp.com"]
CORS_ALLOWED_ORIGINS = [
    "https://project-read-frontend.herokuapp.com",
    "https://getsetlearn.netlify.app",
]

# Redirects all non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = True

# To ensure cookies are only sent with an HTTPS connection
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
