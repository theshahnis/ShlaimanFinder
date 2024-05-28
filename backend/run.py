from app import create_app, mongo
from app.models import User, Group
from flask_cors import CORS

app = create_app()
CORS(app)

@app.shell_context_processor
def make_shell_context():
    return {'db': mongo, 'User': User, 'Group': Group}
    
if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0')