from sqlalchemy import Column, Integer, String, Date, UniqueConstraint
from sqlalchemy.orm import validates
from src.nuvai.core.db import Base
import re
from datetime import date


class EarlyAccessEmail(Base):
    __tablename__ = "early_access_emails"

    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    birth_date = Column(Date, nullable=False)
    location = Column(String(100), nullable=True)

    __table_args__ = (
        UniqueConstraint("email", name="uq_early_access_email"),
    )

    @validates("email")
    def validate_email(self, key, value):
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, value):
            raise ValueError("Invalid email address format")
        return value.strip().lower()

    @validates("first_name", "last_name")
    def validate_name(self, key, value):
        value = value.strip()
        if not value.isalpha() or len(value) < 2:
            raise ValueError(f"Invalid {key.replace('_', ' ')}")
        return value.capitalize()

    @validates("birth_date")
    def validate_birth_date(self, key, value):
        if not isinstance(value, date):
            raise ValueError("Birth date must be a valid date object")
        if value > date.today():
            raise ValueError("Birth date cannot be in the future")
        return value

    @validates("location")
    def validate_location(self, key, value):
        if value:
            value = value.strip()
            if len(value) < 2 or len(value) > 100:
                raise ValueError("Invalid location length")
        return value
