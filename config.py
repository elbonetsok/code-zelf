import os

class Config:
    SECRET_KEY = 'your_secret_key'  # Voeg hier je eigen geheim sleutel toe
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:KlctEw4xeCGGCZNd@aws-0-eu-central-1.pooler.supabase.com:6543/postgres'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Optioneel: voorkomt waarschuwingen
    WTF_CSRF_ENABLED = True
