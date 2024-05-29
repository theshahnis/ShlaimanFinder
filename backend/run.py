from app import create_app, db
from app.models import User, Group
from flask_cors import CORS

app = create_app()
CORS(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Group': Group}
    
app.run(debug=True,host='0.0.0.0')