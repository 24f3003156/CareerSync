from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,UTC

db = SQLAlchemy()

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False )
    pass_hash = db.Column(db.String(100), nullable = False )
    f_name = db.Column(db.String(100), nullable = False)
    l_name = db.Column(db.String(100))
    drives = db.relationship('PlacementDrive', backref = 'company', lazy = True)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    pass_hash = db.Column(db.String(100), nullable = False )
    hr_contact = db.Column(db.Integer, nullable = False)
    website = db.Column(db.String(100), nullable = False)
    domain = db.Column(db.String(100), nullable = False)
    description = db.Column(db.Text, nullable = False)
    approval_status = db.Column(db.String(50), default = "Pending")
    is_active = db.Column(db.Boolean, default = True)
    created_at = db.Column(db.DateTime, default = datetime.now(UTC))
    type_of_employment = db.Column(db.String(100))

class Student(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    full_name = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False, unique = True)
    pass_hash = db.Column(db.String(100), nullable = False )
    phone_number = db.Column(db.Integer, nullable = False)
    degree = db.Column(db.String(100), nullable = False)
    branch = db.Column(db.String(100), nullable = False)
    cgpa = db.Column(db.Float, nullable = False)
    skills = db.Column(db.String(100), nullable = False)
    resume_filename = db.Column(db.String(100), nullable = False)
    is_active = db.Column(db.Boolean, default = True)
    internship_experience = db.Column(db.String(100))
    co_curricular_achievements = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default = datetime.now(UTC))
    applications = db.relationship('Application', backref = 'Student', lazy = True)
    placements = db.relationship('Placement', backref = 'student', lazy = True)

class PlacementDrive(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable = False)
    job_description = db.Column(db.Text, nullable = False)
    skills_required = db.Column(db.String(100), nullable = False)
    package_range = db.Column(db.String(100))
    location = db.Column(db.String(100), nullable = False)
    application_deadline = db.Column(db.DateTime, nullable = False)
    status = db.Column(db.String(50), default = "Pending")
    created_at = db.Column(db.DateTime, default = datetime.now(UTC))
    applications = db.relationship('Application', backref = 'drive', lazy = True)

class Application(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable = False)
    application_date = db.Column(db.DateTime, default = datetime.now(UTC))
    status = db.Column(db.String(50), default = "Applied")
    remarks = db.Column(db.String(100))
    table_args = (db.UniqueConstraint('student_id', 'drive_id', name = 'unique_application'),)

class Placement(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable = False)
    drive_id = db.Column(db.Integer, db.ForeignKey('placement_drive.id'), nullable = False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    placed_on = db.Column(db.DateTime, default = datetime.now(UTC))
    final_status = db.Column(db.String(50), default = "Pending")
    top_50_packages = db.Column(db.Integer, nullable = False)
    drive = db.relationship('PlacementDrive')
    company = db.relationship('Company')