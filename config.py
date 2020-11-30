import os

class Config(object):
    SECRET_KEY= "123"
    DEBUG = False
    USE_RELOADER=False
    SQLALCHEMY_DATABASE_URI= 'mysql://root:ehmonitortest@db:3306/ehmonitor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_UPLOADS = "static/img/mapas"
    ALLOWED_IMAGE_EXTENSIONS = ["JPG", "JPEG"]
    CELERY_BROKER_URL = 'redis://redis:6379'
    CELERY_RESULT_BACKEND = 'redis://redis:6379'
    PERMANENT_SESSION_LIFETIME = 3600

class DevelopmentConfig(Config):
    SECRET_KEY= "123"
    DEBUG = True
    USE_RELOADER=True
    SQLALCHEMY_DATABASE_URI= 'mysql://ehmonitor:ehtest@localhost/ehmonitor'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    IMAGE_UPLOADS = "static/img/mapas"
    ALLOWED_IMAGE_EXTENSIONS = ["JPG", "JPEG"]
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'
    PERMANENT_SESSION_LIFETIME = 3600