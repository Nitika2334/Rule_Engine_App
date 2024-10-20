import os

class Config:

    SECRET_KEY = 'your_secret_key'
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:1525@localhost:5433/RuleEngine'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
