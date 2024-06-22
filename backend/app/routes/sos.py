# sos.py
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from .models import User
from .extensions import db
import requests
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
    #phone_numbers = [member.phone_number for member in group_members if member.phone_number]
    phone_numbers= ["+972547537103"]

    message = f"SOS - Need Assistance\nInitiator: {current_user.username}\nLocation: {current_location}"

    for number in phone_numbers:
        send_sms_or_whatsapp(number, message)

    return jsonify({'message': 'SOS message sent to group members'}), 200

def send_sms_or_whatsapp(phone_number, message):
    # Implement SMS/Whatsapp API call here
    # Example using Twilio (replace with your API details):
    account_sid = 'AC88a7500703d36e12b7a04c25e9d2e3c2'
    auth_token = '7c578ec8c4e13c829b9e087207a6076e'
    from_whatsapp_number = 'whatsapp:+12518108458'
    to_whatsapp_number = f'whatsapp:{phone_number}'
    body = message

    url = f'https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json'
    data = {
        'From': from_whatsapp_number,
        'To': to_whatsapp_number,
        'Body': body
    }
    response = requests.post(url, data=data, auth=(account_sid, auth_token))

    if response.status_code != 201:
        print(f"Failed to send message to {phone_number}: {response.text}")
