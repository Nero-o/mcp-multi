import os
import json
from dotenv import load_dotenv

load_dotenv()


class Config:
    AWS_SQS_QUEUE_URL = os.getenv("AWS_SQS_QUEUE_URL")
    AWS_SQS_QUEUE_URL_CRONJOB = os.getenv("AWS_SQS_QUEUE_URL_CRONJOB")
    AWS_SQS_QUEUE_URL_EMAIL = os.getenv("AWS_SQS_QUEUE_URL_EMAIL")
    AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "risco-sacado-dev")

    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI")
    EXPIRATION_TIME_COOKIE = 60 * 60 * 24

    FLASK_APP = os.getenv("FLASK_APP")
    SECRET_KEY = os.getenv("SECRET_KEY")
    FLASK_RUN_HOST = os.getenv("FLASK_RUN_HOST")
    FLASK_RUN_PORT = os.getenv("FLASK_RUN_PORT")

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

    CLIENT_ID = os.getenv("CLIENT_ID")
    USER_POOL_ID = os.getenv("USER_POOL_ID")

    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    CLIENT_ARGS = {"scope": "openid email"}
    COGNITO_KEYS_URL = os.getenv("COGNITO_KEYS_URL")
    AUTH_URL = os.getenv("AUTH_URL")
    ACCESS_TOKEN_URL = os.getenv("ACCESS_TOKEN_URL")

    AWS_REGION = os.getenv("AWS_REGION")

    REDIS_HOST = os.getenv("REDIS_HOST")
    REDIS_PORT = os.getenv("REDIS_PORT")
    REDIS_USERNAME = os.getenv("REDIS_USERNAME")
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = False
    SESSION_KEY_PREFIX = "session:"
    SESSION_SERIALIZER = json  # Adicione esta linha
    # SQLALCHEMY_DATABASE_URI =
