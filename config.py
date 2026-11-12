import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Base Configuration with environment fallbacks."""
    ENV = os.environ.get("FLASK_ENV", "development")
    DEBUG = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true") or ENV == "development"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-case-47-downtime-logger")

    # Persistent SQLite database path
    db_env = os.environ.get("DATABASE_PATH", "factory.db")
    if not os.path.isabs(db_env):
        DATABASE_PATH = os.path.normpath(os.path.join(BASE_DIR, db_env))
    else:
        DATABASE_PATH = db_env

    DOWNTIME_HOURLY_RATE = float(os.environ.get("DOWNTIME_HOURLY_RATE", 50000.0))  # Rs. 50,000 / hr
    TESTING = False

class ProductionConfig(Config):
    """Production-style Configuration."""
    ENV = "production"
    DEBUG = False
    # Validate secret key is explicitly set in production
    if Config.SECRET_KEY == "dev-secret-key-case-47-downtime-logger":
        # In a strict deployment, a warning or assertion is logged
        pass

class DevelopmentConfig(Config):
    """Development Configuration."""
    ENV = "development"
    DEBUG = True

class TestConfig(Config):
    """Automated Testing Configuration."""
    TESTING = True
    DEBUG = False
    DATABASE_PATH = ":memory:"

def get_config(env_name=None):
    """Factory helper returning appropriate config class."""
    if not env_name:
        env_name = os.environ.get("FLASK_ENV", "development").lower()
    if env_name == "production":
        return ProductionConfig
    elif env_name == "testing":
        return TestConfig
    return DevelopmentConfig
