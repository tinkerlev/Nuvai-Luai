# File: upload_logo.py

import os
import uuid
import hashlib
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from src.nuvai.models.user import User
from src.nuvai.utils.logger import get_logger
from src.nuvai.core.db import db_session
from PIL import Image

logger = get_logger("UploadLogo")
upload_logo_bp = Blueprint('upload_logo', __name__)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 2 * 1024 * 1024
UPLOAD_FOLDER = os.path.join("secure_user_logos")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@upload_logo_bp.route('/api/users/upload-logo', methods=['POST'])
@jwt_required()
def upload_logo():
    user_email = get_jwt_identity()
    file = request.files.get('logo')

    if not file or file.filename == '':
        return jsonify({'status': 'error', 'message': 'No file provided'}), 400

    if not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': 'Invalid file type'}), 400

    if not file.mimetype.startswith("image/"):
        return jsonify({'status': 'error', 'message': 'Invalid MIME type'}), 400

    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)

    if file_length > MAX_FILE_SIZE:
        return jsonify({'status': 'error', 'message': 'File too large'}), 413

    temp_filename = f"temp_{uuid.uuid4().hex}.tmp"
    temp_path = os.path.join(UPLOAD_FOLDER, temp_filename)
    file.save(temp_path)

    try:
        with Image.open(temp_path) as img:
            img.verify()
            img_format = img.format.lower()
            if img_format not in ALLOWED_EXTENSIONS:
                os.remove(temp_path)
                return jsonify({'status': 'error', 'message': 'Unsupported image format'}), 400
    except Exception:
        os.remove(temp_path)
        return jsonify({'status': 'error', 'message': 'Corrupted or invalid image'}), 400

    try:
        with Image.open(temp_path) as img:
            data = list(img.getdata())
            clean_img = Image.new(img.mode, img.size)
            clean_img.putdata(data)
            email_hash = hashlib.sha256(user_email.encode()).hexdigest()
            final_filename = f"{email_hash}_{uuid.uuid4().hex}.png"
            final_path = os.path.join(UPLOAD_FOLDER, final_filename)
            clean_img.save(final_path, format="PNG")
    except Exception as e:
        logger.error(f"Image processing error: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return jsonify({'status': 'error', 'message': 'Image processing failed'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

    with db_session() as session:
        user = session.query(User).filter_by(email=user_email).first()
        if user.logo_path:
            try:
                old_path = os.path.join(UPLOAD_FOLDER, os.path.basename(user.logo_path))
                if os.path.exists(old_path):
                    os.remove(old_path)
            except Exception as e:
                logger.warning(f"Failed to remove old logo: {e}")
        user.logo_path = f"/user-logo/{final_filename}"
        session.commit()
        logger.info(f"Logo uploaded for {user.email}")

    return jsonify({
        'status': 'success',
        'message': 'Logo uploaded',
        'path': user.logo_path
    }), 200
