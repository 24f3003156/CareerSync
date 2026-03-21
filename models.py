from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,UTC

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
    created_at = db.Column(db.datetime, default = datetime.now(UTC))
    type_of_employment = db.Column(db.string(100))

class Student(db.Model):
    id = db.Column(db.integer, primary_key = True)
    full_name = db.Column(db.string(100), nullable = False)
    email = db.Column(db.string, nullable = False, unique = True)
    pass_hash = db.Column(db.string(100), nullable = False )
    phone_number = db.Column(db.integer, nullable = False)
    degree = db.Column(db.string(100), nullable = False)
    branch = db.Column(db.string(100), nullable = False)
    cgpa = db.Column(db.float, nullable = False)
    skills = db.Column(db.string(100), nullable = False)
    resume_filename = db.Column(db.string(100), nullable = False)
    is_active = db.Column(db.boolean, default = True)
    internship_experience = db.Column(db.string(100))
    co-curricular_achievements = db.Column(db.string(100))

class PlacementDrive(db.Model):
    id = db.Column(db.integer, primary_key = True)
    company_id = db.Column(db.integer, db.ForeignKey('Company.id'), nullable=False)
    job_title = db.Column(db.string(100), nullable = False)
    job_description = db.Column(db.text, nullable = False)
    skills_required = db.Column(db.string(100), nullable = False)
    package_range = db.Column(db.string(100))
    location = db.Column(db.string(100), nullable = False)
    application_deadline = db.Column(db.datetime, nullable = False)
    status = db.Column(db.string(50), default = "Pending")
    created_at = db.Column(db.datetime, default = datetime.now(UTC))

class Application(db.Model):
    id = db.Column(db.integer, primary_key = True)
    student_id = db.Column(db.integer, db.ForeignKey('Student.id'), nullable = False)
    drive_id = db.Column(db.integer, db.ForeignKey('PlacementDrive.id'), nullable = False)
    application_date = db.Column(db.datetime, default = datetime.now(UTC))
    status = db.Column(db.string(50), default = "Applied ")
    remarks = db.Column(db.string(100))

class Placement(db.Model):
    id = db.Column(db.integer, primary_key = True)
    student_id = db.Column(db.integer, db.ForeignKey('Student.id'), nullable = False)
    drive_id = db.Column(db.integer, db.ForeignKey('PlacementDrive.id'), nullable = False)
    company_id = db.Column(db.integer, db.ForeignKey('Company.id'), nullable=False)
    placed_on = db.Column(db.datetime, default = datetime.now(UTC))
    final_status = db.Column(db.string(50), default = "Pending")
    top_50_packages = db.Column(db.integer, nullable = False)
 




    












