from flask.cli import FlaskGroup
from flask_migrate import Migrate
from app import create_app
from app.extensions import db

app = create_app()
cli = FlaskGroup(create_app=create_app)

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    cli()
