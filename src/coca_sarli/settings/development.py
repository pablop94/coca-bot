from .base import *  # noqa: F401

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "docker",
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}
