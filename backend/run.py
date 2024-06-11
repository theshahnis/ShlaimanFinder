from app import create_app, db
from app.models import User, Group
from flask_cors import CORS
import os

app = create_app()
CORS(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Group': Group}

if __name__ == '__main__':
    # Run the app with SSL context
    app.run(debug=True, host='0.0.0.0', ssl_context=('certs/cert.pem', 'certs/key.pem'))
