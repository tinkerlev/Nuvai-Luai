from datetime import datetime, timezone
from enum import Enum
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime,
    Enum as SqlEnum
)
from sqlalchemy.orm import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash
from src.nuvai.core.db import Base, db_session
from src.nuvai.utils.logger import get_logger

logger = get_logger("UserModel")


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)
    
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    plan = Column(String(20), default="free", nullable=False)
    
    is_verified = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True)
    failed_logins = Column(Integer, default=0)
    last_login = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def set_password(self, raw_password: str):
        """Hashes and stores the user's password securely."""
        self.password = generate_password_hash(raw_password)
        logger.debug(f"Password hashed for user {self.email}")

    def check_password(self, raw_password: str) -> bool:
        """Validates a plain password against the hashed version."""
        return check_password_hash(self.password, raw_password)

    def mark_login_success(self):
        self.last_login = datetime.now(timezone.utc)
        self.failed_logins = 0
        logger.info(f"Successful login recorded for user {self.email}")

    def mark_login_failure(self):
        self.failed_logins += 1
        logger.warning(f"Failed login attempt #{self.failed_logins} for {self.email}")
        if self.failed_logins >= 5:
            self.lock_account()

    def lock_account(self):
        self.is_active = False
        logger.critical(f"Account locked due to repeated failures: {self.email}")

    def save(self):
        """Saves or updates the user in the database."""
        try:
            with db_session() as session:
                session.add(self)
                session.commit()
                logger.info(f"User {self.email} saved.")
        except Exception as e:
            logger.error(f"DB error saving user {self.email}: {str(e)}")
            raise

    def delete(self):
        try:
            with db_session() as session:
                session.delete(self)
                session.commit()
                logger.info(f"User {self.email} deleted.")
        except Exception as e:
            logger.error(f"DB error deleting user {self.email}: {str(e)}")
            raise

    @staticmethod
    def get_by_email(email: str):
        with db_session() as session:
            return session.query(User).filter_by(email=email).first()

    def __repr__(self):
        return f"<User(email={self.email}, verified={self.is_verified}, active={self.is_active})>"
