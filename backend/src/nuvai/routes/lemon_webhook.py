# lemon_webhook.py

import os
import hmac
import hashlib
import logging
from flask import Blueprint, request, jsonify, abort
from src.nuvai.models.user import User

lemon_webhook = Blueprint("lemon_webhook", __name__)
logger = logging.getLogger(__name__)

SIGNING_SECRET = os.getenv("LEMON_WEBHOOK_SECRET")

SOLO_MONTHLY_ID = int(os.getenv("LEMON_SOLO_MONTHLY_PRODUCT_ID", "0"))
SOLO_YEARLY_ID = int(os.getenv("LEMON_SOLO_YEARLY_PRODUCT_ID", "0"))
PRO_BUSINESS_ID = int(os.getenv("LEMON_PRO_BUSINESS_PRODUCT_ID", "0"))
FREE_PLAN_ID = int(os.getenv("LEMON_FREE_PLAN_PRODUCT_ID", "0"))

def verify_lemon_signature(req):
    signature = req.headers.get("X-Signature")
    if not signature:
        logger.warning("Missing X-Signature header")
        abort(400, "Missing signature")

    payload = req.get_data()
    expected = hmac.new(
        SIGNING_SECRET.encode(),
        msg=payload,
        digestmod=hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        logger.warning("Signature mismatch")
        abort(403, "Invalid signature")

@lemon_webhook.route("/webhook/lemon", methods=["POST"])
def handle_lemon_webhook():
    verify_lemon_signature(request)
    payload = request.get_json()

    event = payload.get("meta", {}).get("event_name")
    data = payload.get("data", {}).get("attributes", {})

    if event == "order_created":
        email = data.get("user_email")
        product_id = data.get("product_id")
        order_id = data.get("id")

        logger.info(f"[LemonSqueezy] Order received: {email} / product_id: {product_id} / order_id: {order_id}")

        if email and product_id:
            try:
                user = User.get_by_email(email)
                if not user:
                    logger.warning(f"⚠️ Webhook received for unknown user: {email} — ignoring")
                    return jsonify({"status": "user_not_found"}), 404

                if product_id == SOLO_MONTHLY_ID:
                    user.plan = "solo_monthly"
                elif product_id == SOLO_YEARLY_ID:
                    user.plan = "solo_yearly"
                elif product_id == PRO_BUSINESS_ID:
                    user.plan = "pro_business"
                elif product_id == FREE_PLAN_ID:
                    user.plan = "free"
                else:
                    logger.warning(f"⚠️ Unknown product_id {product_id} for user {email}")
                    return jsonify({"status": "unknown_product"}), 400

                user.save()
                logger.info(f"✅ User {email} upgraded to plan: {user.plan}")
                return jsonify({"status": "user_upgraded"}), 200

            except Exception as e:
                logger.error(f"❌ Failed to update user {email}: {e}")
                return jsonify({"status": "error"}), 500

        return jsonify({"status": "missing_data"}), 400

    return jsonify({"status": "ignored"}), 200
