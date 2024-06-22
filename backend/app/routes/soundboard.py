from flask import Blueprint, render_template, request, jsonify, current_app, send_from_directory
from werkzeug.utils import secure_filename
import os
from .api import token_or_login_required

soundboard_bp = Blueprint('soundboard_bp', __name__)

SOUND_UPLOAD_FOLDER = 'static/sounds'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

@soundboard_bp.route('/')
@token_or_login_required
def soundboard_page():
    try:
        sound_files = os.listdir(os.path.join(current_app.root_path, SOUND_UPLOAD_FOLDER))
        return render_template('soundboard.html', sound_files=sound_files)
    except Exception as e:
        return jsonify({'message': 'Failed to load sounds', 'error': str(e)}), 500

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@soundboard_bp.route('/upload', methods=['POST'])
@token_or_login_required
def upload_sound():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.root_path, SOUND_UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'message': 'Invalid file type'}), 400

@soundboard_bp.route('/get_sounds', methods=['GET'])
@token_or_login_required
def list_sounds():
    try:
        sound_files = os.listdir(os.path.join(current_app.root_path, SOUND_UPLOAD_FOLDER))
        return jsonify({'sounds': sound_files}), 200
    except Exception as e:
        return jsonify({'message': 'Failed to list sounds', 'error': str(e)}), 500

@soundboard_bp.route('/get_sounds/<filename>', methods=['GET'])
@token_or_login_required
def get_sound(filename):
    try:
        return send_from_directory(os.path.join(current_app.root_path, SOUND_UPLOAD_FOLDER), filename)
    except Exception as e:
        return jsonify({'message': 'Failed to fetch sound', 'error': str(e)}), 500
