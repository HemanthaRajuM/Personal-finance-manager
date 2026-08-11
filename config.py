import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_USER = os.environ.get("MYSQL_USER")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    MYSQL_DB = os.environ.get("MYSQL_DB", "findb")
    MYSQL_CURSORCLASS = "DictCursor"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("FLASK_ENV") == "production"

    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise RuntimeError("FLASK_SECRET_KEY must be configured")
        required = {
            "MYSQL_USER": cls.MYSQL_USER,
            "MYSQL_PASSWORD": cls.MYSQL_PASSWORD,
        }
        missing = [name for name, value in required.items() if not value]
        if missing:
            raise RuntimeError(f"Missing configuration: {', '.join(missing)}")
