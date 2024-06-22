# sos.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import User
from app.extensions import db
import os
from twilio.rest import Client
from dotenv import load_dotenv
from .api import token_or_login_required

load_dotenv()

import logging
from logging.handlers import RotatingFileHandler

ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
ACCOUNT_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
handler = RotatingFileHandler('sos.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)

sos_bp = Blueprint('sos_bp', __name__)

@sos_bp.route('/')
@token_or_login_required
def sos_page():
    return render_template('sos.html')

@sos_bp.route('/send_sos', methods=['POST'])
@token_or_login_required
def send_sos():
    try:
        data = request.get_json()
        latitude = data.get('latitude', None)
        longitude = data.get('longitude', None)
        if not latitude or not longitude:
            logger.error('Coordinates not provided')
            return jsonify({'message': 'Coordinates not provided'}), 400

        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        current_location = google_maps_link
        logger.debug(f"Google Maps Link: {google_maps_link}")

        group_id = current_user.group_id
        if not group_id:
            logger.error('User is not part of any group')
            return jsonify({'message': 'You are not part of any group'}), 400

        # Query group members with phone numbers
        group_members = User.query.filter_by(group_id=group_id).all()
        phone_numbers = [member.phone_number for member in group_members if member.phone_number]

        # Query all users with phone numbers if not already included
        all_users_with_phone_numbers = User.query.filter(User.phone_number.isnot(None)).all()
        all_phone_numbers = {user.phone_number for user in all_users_with_phone_numbers}

        # Combine and deduplicate phone numbers
        phone_numbers = list(set(phone_numbers) | all_phone_numbers)

        # Fallback for testing purposes
        if not phone_numbers:
            phone_numbers = ["+972547537103"]

        message_template_name = 'sos_alert'
        initiator_username = current_user.username
        initiator_number = current_user.number if current_user.number else 'missing'
        logger.debug(f"Initiator: {initiator_username}, Phone: {initiator_number}")

        for number in phone_numbers:
            logger.debug(f"Sending message to: {number}")
            send_sms_or_whatsapp(number, message_template_name, initiator_username, current_location, initiator_number)

        return jsonify({'message': 'SOS message sent to group members and all users with phone numbers'}), 200
    except Exception as e:
        logger.error(f"Error in send_sos: {e}", exc_info=True)
        return jsonify({'message': 'Failed to send SOS message'}), 500

def send_sms_or_whatsapp(phone_number, template_name, initiator_username, location, initiator_number):
    try:
        # Check if the Twilio credentials are loaded
        if not ACCOUNT_SID or not ACCOUNT_TOKEN:
            logger.error("Twilio account SID or auth token not set")
            return

        client = Client(ACCOUNT_SID, ACCOUNT_TOKEN)

        from_whatsapp_number = 'whatsapp:+12518108458'
        to_whatsapp_number = f'whatsapp:{phone_number}'

        body_params = [initiator_username, location, initiator_number]
        logger.debug(f"Body Params: {body_params}")

        # Send message using the template
        message = client.messages.create(
            from_=from_whatsapp_number,
            to=to_whatsapp_number,
            body=f"SOS - Need Assistance\nInitiator: {initiator_username}\nLocation: {location}\nPhone: {initiator_number}",  # Include a fallback message body
            status_callback='http://yourserver.com/twilio_status_callback',  # Update this to your actual status callback URL
            persistent_action=[
                {
                    "type": "template",
                    "template_name": template_name,
                    "template_language": "en",
                    "body_params": body_params
                }
            ]
        )

        logger.debug(f"Message SID: {message.sid}")

    except Exception as e:
        logger.error(f"Error sending message using Twilio: {e}", exc_info=True)