# sos.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import User
from app.extensions import db
import os
from twilio.rest import Client
from .api import token_or_login_required

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
            return jsonify({'message': 'Coordinates not provided'}), 400

        google_maps_link = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
        current_location = google_maps_link

        group_id = current_user.group_id
        if not group_id:
            return jsonify({'message': 'You are not part of any group'}), 400

        group_members = User.query.filter_by(group_id=group_id).all()
        #phone_numbers = [member.phone_number for member in group_members if member.phone_number]
        phone_numbers = ["+972547537103"]  # For testing purposes

        message_template_name = 'sos_alert'
        initiator_username = current_user.username

        for number in phone_numbers:
            send_sms_or_whatsapp(number, message_template_name, initiator_username, current_location)

        return jsonify({'message': 'SOS message sent to group members'}), 200
    except Exception as e:
        print(f"Error sending initiate send sms: {e}")
def send_sms_or_whatsapp(phone_number, template_name, initiator_username, location):
    try:
        account_sid = os.getenv('ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        client = Client(account_sid, auth_token)

        from_whatsapp_number = 'whatsapp:+12518108458'
        to_whatsapp_number = f'whatsapp:{phone_number}'

        body_params = [initiator_username, location]

        message = client.messages.create(
            from_=from_whatsapp_number,
            to=to_whatsapp_number,
            provide_feedback=True,
            persistent_action=[
                {
                    "type": "template",
                    "template_name": template_name,
                    "template_language": "en",  # Adjust language code if necessary
                    "body_params": body_params
                }
            ]
        )

        print(f"Message SID: {message.sid}")

    except Exception as e:
        print(f"Error sending message using Twilio: {e}")
