from flask import Blueprint, request, jsonify, url_for, current_app
from werkzeug.utils import secure_filename
import os

sounds_bp = Blueprint('sounds_bp', __name__)

SOUND_UPLOAD_FOLDER = 'static/sounds'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@sounds_bp.route('/upload', methods=['POST'])
def upload_sound():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.root_path, UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 200
    return jsonify({'message': 'Invalid file type'}), 400

@sounds_bp.route('/sounds', methods=['GET'])
def list_sounds():
    sound_files = os.listdir(os.path.join(current_app.root_path, UPLOAD_FOLDER))
    return jsonify({'sounds': sound_files}), 200