from urllib.parse import urlparse

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

GITHUB_HOSTS = {"github.com", "www.github.com"}


def validate_github_url(value):
    validator = URLValidator(schemes=["http", "https"])
    validator(value)
    host = urlparse(value).hostname or ""
    if host.lower() not in GITHUB_HOSTS:
        raise ValidationError("Ссылка должна вести на github.com.")
