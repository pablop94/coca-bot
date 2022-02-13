from .base import *  # noqa: F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "dbtest",
        "USER": "postgres",
        "PASSWORD": "docker",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
