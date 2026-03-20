from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.integer, primary_key = True)
    username = db.Column(db.string(100), unique = True, nullable = False )
    pass_hash = db.Column(db.string(100), nullable = False )
    f_name = db.Column(db.string(100), nullable = False)
    l_name = db.Column(db.string(100))

class Company(db.Model):
    id = db.Column(db.integer, primary_key = True)
    company_name = db.Column(db.string(100), nullable = False)
    email = db.Column(db.string, nullable = False, unique = True)
    pass_hash = db.Column(db.string(100), nullable = False )
    hr_contact = db.Column(db.integer, nullable = False)
    website = db.Column(db.string(100), nullable = False)
    domain = db.Column(db.string(100), nullable = False)
    description = db.Column(db.text, nullable = False)
    approval_status = db.Column(db.string(50), default = "Pending")
    is_active = db.Column(db.boolean, default = True)
    created_at = db.Column(db.datetime, default = datetime.utcnow)
    type_of_employment = db.Column(db.string(100))




