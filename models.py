from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.integer, primary_key = True)
    username = db.Column(db.string(100), unique = True, nullable = False )
    pass_hash = db.Column(db.string(100), nullable = False )
    f_name = db.Column(db.string(100), nullable = False)
    l_name = db.Column(db.string(100))
