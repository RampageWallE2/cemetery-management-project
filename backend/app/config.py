import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

class Config:

        SQLALCHEMY_DATABASE_URI = (
                f"postgresql+psycopg2://"
                f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
                f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
                )


        SQLALCHEMY_TRACK_MODIFICATIONS = False

        JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

        JWT_ACCESS_TOKEN_EXPIRES = timedelta(
                minutes=int(os.getenv("JWT_ACCESS_TOKEN_MINUTES", "60"))
    )