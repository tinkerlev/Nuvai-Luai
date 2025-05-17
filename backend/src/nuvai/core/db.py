import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session

# === Load environment variables securely ===
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv()

# === Set environment mode ===
ENVIRONMENT = os.getenv("ENVIRONMENT", "production").lower()

# === Configure logger ===
logger = logging.getLogger("DatabaseCore")
logger.setLevel(logging.DEBUG if ENVIRONMENT == "development" else logging.WARNING)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

if ENVIRONMENT == "development":
    logger.info("🔐 .env file loaded successfully.")

# === Define Base ORM class ===
Base = declarative_base()

# === Load database URL ===
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    logger.critical("❌ DATABASE_URL is not set.")
    raise EnvironmentError("Missing DATABASE_URL in environment variables.")

# === Initialize SQLAlchemy engine ===
try:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"connect_timeout": 10},
        future=True,
    )
    logger.info("✅ SQLAlchemy engine initialized.")
except Exception as e:
    logger.exception("❌ Failed to initialize SQLAlchemy engine.")
    raise e

# === Configure scoped session ===
db_session = scoped_session(
    sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
)

# === Dependency injection helper ===
def get_db():
    db = db_session()
    try:
        yield db
    except Exception as e:
        logger.exception("❌ Exception during DB session.")
        raise e
    finally:
        db.close()

# === Initialize DB schema ===
def init_db():
    try:
        from src.nuvai.models import early_access
        Base.metadata.create_all(bind=engine)
        logger.info("📦 Database schema created.")
    except Exception as e:
        logger.exception("❌ Failed to create database schema.")
        raise e
