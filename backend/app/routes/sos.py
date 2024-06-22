# sos.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.models import User
from app.extensions import db
import requests
import os
from .api import token_or_login_required

sos_bp = Blueprint('sos_bp', __name__)

@sos_bp.route('/')
@token_or_login_required
def sos_page():
    return render_template('sos.html')

@sos_bp.route('/send_sos', methods=['POST'])
@token_or_login_required
def send_sos():
    data = request.get_json()
    current_location = data.get('location', 'Location not provided')

    group_id = current_user.group_id
    if not group_id:
        return jsonify({'message': 'You are not part of any group'}), 400

    group_members = User.query.filter_by(group_id=group_id).all()
    # phone_numbers = [member.phone_number for member in group_members if member.phone_number]
    phone_numbers = ['+972547537103']

    message = f"SOS - Need Assistance\nInitiator: {current_user.username}\nLocation: {current_location}"

    for number in phone_numbers:
        print(f"trying to send message to {number}")
        send_sms_or_whatsapp(number, message)

    return jsonify({'message': f'SOS message sent to group members by {current_user.username} to {phone_numbers}'}), 200

def send_sms_or_whatsapp(phone_number, message):
    try:
        account_sid = os.getenv('ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_whatsapp_number = 'whatsapp:+12518108458'
        to_whatsapp_number = f'whatsapp:{phone_number}'
        body = message

        # Logging the environment variables and request data
        print(f"Account SID: {account_sid}")
        print(f"Auth Token: {auth_token}")
        print(f"From: {from_whatsapp_number}")
        print(f"To: {to_whatsapp_number}")
        print(f"Body: {body}")

        url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
        data = {
            'From': from_whatsapp_number,
            'To': to_whatsapp_number,
            'Body': body
        }
        response = requests.post(url, data=data, auth=(account_sid, auth_token))

        # Logging the response
        print(f"Twilio Response Status: {response.status_code}")
        print(f"Twilio Response Text: {response.text}")

        if response.status_code != 201:
            print(f"Failed to send message to {phone_number}: {response.text}")
    except Exception as e:
        print(f"Error sending message using Twilio: {e}")
