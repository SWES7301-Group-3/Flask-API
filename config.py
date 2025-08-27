import os
from dotenv import load_dotenv

load_dotenv()  # load variables from .env

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
    DEBUG = True
