from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from turbo_flask import Turbo

db = SQLAlchemy()
turbo = Turbo()
cors = CORS() 