from .base import *  # noqa: F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbtest",
        "USER": "postgres",
        "PASSWORD": "docker",
        "HOST": "postgres",
        "PORT": "5432",
    }
}
