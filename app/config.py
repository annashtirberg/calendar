# flake8: noqa
from typing import Tuple

from pydantic import BaseSettings

# DATABASE
DEVELOPMENT_DATABASE_STRING = "sqlite:///./dev.db"

# MEDIA
MEDIA_DIRECTORY = 'media'
PICTURE_EXTENSION = '.png'
AVATAR_SIZE = (120, 120)


class Settings(BaseSettings):
    # DATABASE
    database_connection_string: str = DEVELOPMENT_DATABASE_STRING
    # MEDIA
    media_directory: str = MEDIA_DIRECTORY
    media_picture_extension: str = PICTURE_EXTENSION
    media_avatar_size: Tuple[int, int] = AVATAR_SIZE
    # EMAILS
    smtp_username: str = "no-username"
    smtp_password: str = "no-password"
    smtp_from_email: str = "invite@calendar-app.com"
    smtp_port: int = 3999
    smtp_server: str = "localhost"
    smtp_use_tls: bool = False
    smtp_use_ssl: bool = False
    smtp_use_credentials: bool = False


def get_settings():
    return Settings()
