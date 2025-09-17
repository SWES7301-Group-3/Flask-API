import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///api.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-super-secret')
    DEBUG = True
    
    # Django integration settings
    DJANGO_API_URL = os.environ.get('DJANGO_API_URL', 'http://localhost:8000')
    DJANGO_VERIFY_TOKEN_ENDPOINT = '/subscriptions/verify-token/'
    
    # API Documentation settings
    API_TITLE = 'Environmental Data API'
    API_VERSION = '1.0'
    API_DESCRIPTION = 'Subscription-based environmental data API with tiered access'