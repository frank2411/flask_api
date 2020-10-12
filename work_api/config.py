import os
from dotenv import load_dotenv

load_dotenv()


class BaseConfig:
    ENV = os.getenv('FLASK_ENV')
    SECRET_KEY = os.getenv('SECRET_KEY', "localkey")


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False

    DB_ENGINE = os.getenv("DB_ENGINE")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class DevelopConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DB_ENGINE = os.getenv("DB_ENGINE")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")

    SQLALCHEMY_DATABASE_URI = f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class LocalConfig(BaseConfig):
    DEBUG = True
    TESTING = False

    DB_ENGINE = os.getenv("DB_ENGINE", "postgresql")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "backend")

    SQLALCHEMY_DATABASE_URI = f'{DB_ENGINE}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'


class TestConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:admin@localhost:5432/worklife_test_database"
