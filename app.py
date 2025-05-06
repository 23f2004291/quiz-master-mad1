from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config  # Import configuration class

app = Flask(__name__)
app.config.from_object(Config)  # Load configurations

from models import *
if __name__ == "__main__":
    app.run(debug=True)
