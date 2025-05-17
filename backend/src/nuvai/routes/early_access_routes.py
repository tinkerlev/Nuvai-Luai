from flask import Blueprint, request, jsonify
from datetime import datetime, date
from backend.src.nuvai.utils.logger import get_logger
from backend.src.utils.sanitize import sanitize_email, sanitize_text
from backend.src.nuvai.models.early_access import EarlyAccessEmail
from backend.src.nuvai.core.db import db_session

logger = get_logger(__name__)
early_access_blueprint = Blueprint("early_access", __name__)

@early_access_blueprint.route("/api/early-access", methods=["POST"])
def register_early_access():
    try:
        data = request.get_json(force=True)

        email_raw = data.get("email", "").strip()
        first_name_raw = data.get("first_name", "").strip()
        last_name_raw = data.get("last_name", "").strip()
        birth_date_raw = data.get("birth_date", "").strip()
        location_raw = data.get("location", "").strip()

        # Required field checks
        if not email_raw or not first_name_raw or not last_name_raw or not birth_date_raw:
            return jsonify({"error": "Missing required fields."}), 400

        email = sanitize_email(email_raw)
        first_name = sanitize_text(first_name_raw)
        last_name = sanitize_text(last_name_raw)
        location = sanitize_text(location_raw) if location_raw else None

        try:
            birth_date = datetime.strptime(birth_date_raw, "%Y-%m-%d").date()
            if birth_date > date.today():
                raise ValueError("Birth date can't be in the future")
        except ValueError as e:
            return jsonify({"error": str(e)}), 400

        # Check for duplicate without disclosing it to the user
        existing_entry = db_session.query(EarlyAccessEmail).filter_by(email=email).first()
        if existing_entry:
            logger.info(f"[EarlyAccess] Repeated registration attempt for: {email}")
            return jsonify({"message": "Thank you! You're on the early access list."}), 200

        # Register new user
        new_entry = EarlyAccessEmail(
            email=email,
            first_name=first_name,
            last_name=last_name,
            birth_date=birth_date,
            location=location
        )

        db_session.add(new_entry)
        db_session.commit()

        logger.info(f"[EarlyAccess] New early access user registered: {email}")
        return jsonify({"message": "Thank you! You're on the early access list."}), 201

    except Exception as e:
        logger.error(f"[EarlyAccess] Registration error: {str(e)}")
        return jsonify({"error": "An error occurred. Please try again later."}), 500
