from flask import Blueprint, render_template
from flask_login import login_required, current_user

map_bp = Blueprint('map_bp', __name__)

@map_bp.route('/', methods=['GET'])
@login_required
def map_view():
    return render_template('map.html')
