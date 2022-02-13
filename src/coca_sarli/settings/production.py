import dj_database_url
from .base import *  # noqa: F401

DEBUG = False

DATABASES = {"default": dj_database_url.config()}
