from flask import Flask, render_template, request, redirect, url_for, flash, session 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Company, Student, PlacementDrive, Application, Placement

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "career_sync_secret"

db.init_app(app)

def admin_logged_in():
    return "user_id" in session and session.get("role") =="admin"

def company_logged_in():
    return "user_id" in session and session.get("role") =="company"

def student_logged_in():
    return "user_id" in session and session.get("role") =="student"


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role")
        email_or_username = request.form.get("email_or_username")
        password = request.form.get("password")

        if role == "admin":
            admin = Admin.query.filter_by(username = email_or_username).first()
            if admin and check_password_hash(admin.pass_hash, password):
                session["user_id"] = admin.id
                session["role"] = "admin"
                flash("Admin login successful.")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid admin credentials.")

        elif role == "company":
            company = Company.query.filter_by(email = email_or_username).first()
            if company and check_password_hash(company.pass_hash, password):

                if company.approval_status != "Approved":
                    flash("Company not yet approved by admin.")
                    return redirect(url_for("login"))
                
                if company.is_active == False:
                    flash("Company account is deactivated.")
                    return redirect(url_for("login"))
                
                session["user_id"] = company.id
                session["role"] = "company"
                flash("Company login successful.")
                return redirect(url_for("company_dashboard"))
            else:
                flash("Invalid company credentials.")

        elif role == "student":
            student = Student.query.filter_by(email = email_or_username).first()
            if student and check_password_hash(student.pass_hash, password):
                if student.is_active == False:
                    flash("Student account is deactivated.")
                    return redirect(url_for("login"))
                session["user_id"] = student.id
                session["role"] = "student"
                flash("Student login successful.")
                return redirect(url_for("student_dashboard"))
            else:
                 flash("Invalid student credentials.")

        else:
            flash("Select a valid role.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for("login"))

@app.route("/register/company", methods = ["GET", "POST"])
def register_company():
    if request.method == "POST":
        company_name = request.form.get("company_name")
        email = request.form.get("email")
        password = request.form.get("password")
        hr_contact = int(request.form.get("hr_contact"))
        website = request.form.get("website")
        domain = request.form.get("domain")
        description = request.form.get("description")
        type_of_employment = request.form.get("type_of_employment")

        existing_company = Company.query.filter_by(email = email).first()

        if existing_company:
            flash("Company already registered.")
            return redirect(url_for("register_company"))
        
        new_company = Company(
            company_name = company_name,
            email = email,
            pass_hash = generate_password_hash(password),
            hr_contact = hr_contact,
            website = website,
            domain = domain,
            description = description,
            type_of_employment = type_of_employment
        )

        db.session.add(new_company)
        db.session.commit()
        flash("Company registration was successfully submitted.")
        return redirect(url_for("login"))
    return render_template("register_company.html")
   
@app.route("/register/student", methods = ["GET", "POST"])
def register_student():
    if request.method == "POST":
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        password = request.form.get("password")
        phone_number = int(request.form.get("phone_number"))
        degree = request.form.get("degree")
        branch = request.form.get("branch")
        cgpa = float(request.form.get("cgpa"))
        skills = request.form.get("skills")
        resume_filename = request.form.get("resume_filename")
        internship_experience = request.form.get("internship_experience")
        co_curricular_achievements = request.form.get("co_curricular_achievements")

        existing_student = Student.query.filter_by(email = email).first()

        if existing_student:
            flash("Student already registered.")
            return redirect(url_for("register_student"))
        
        new_student = Student(
            full_name = full_name,
            email = email,
            pass_hash = generate_password_hash(password),
            phone_number = phone_number,
            degree = degree, 
            branch = branch,
            cgpa = cgpa,
            skills = skills,
            resume_filename = resume_filename,
            internship_experience = internship_experience,
            co_curricular_achievements = co_curricular_achievements
        )

        db.session.add(new_student)
        db.session.commit()
        flash("Student registered successfully.")
        return redirect(url_for("login"))
    
    return render_template("register_student.html")

@app.route("/admin/applications")
def admin_applications():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    applications = Application.query.all()
    return render_template("admin_applications.html", applications = applications)

@app.route("/admin/placements")
def admin_placements():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    placements = Placement.query.all()
    return render_template("admin_placements.html", placements = placements)

@app.route("/admin/dashboard")
def admin_dashboard():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    total_companies = Company.query.count()
    total_students = Student.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    return render_template("admin_dashboard.html", total_companies = total_companies, total_students = total_students, total_drives = total_drives, total_applications = total_applications)

@app.route("/admin/companies")
def admin_companies():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    search_query = request.args.get("search")
    if search_query:
        companies = Company.query.filter(
            (Company.company_name.ilike(f"%{search_query}%"))|
            (Company.email.ilike(f"%{search_query}%"))|
            (Company.domain.ilike(f"%{search_query}%"))
        ).all()
    else:
        companies = Company.query.all()
    return render_template("admin_companies.html", companies =companies)

@app.route("/admin/company/<int:company_id>/approve")
def approve_company(company_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Approved"
    company.is_active = True
    db.session.commit()
    flash("Company approved successfully.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/company/<int:company_id>/reject")
def reject_company(company_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Rejected"    
    db.session.commit()
    flash("Company rejected successfully.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/company/<int:company_id>/blacklist")
def blacklist_company(company_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    company = Company.query.get_or_404(company_id)
    company.approval_status = "Blacklisted"
    company.is_active = False
    db.session.commit()
    flash("Company blacklisted successfully.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/drives")
def admin_drives():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drives = PlacementDrive.query.all()
    return render_template("admin_drives.html", drives = drives)

@app.route("/admin/drive/<int:drive_id>/approve")
def approve_drive(drive_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Approved"
    db.session.commit()
    flash("Placement drive approved successfully.")
    return redirect(url_for("admin_drives"))

@app.route("/admin/drive/<int:drive_id>/reject")
def reject_drive(drive_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = "Rejected"
    db.session.commit()
    flash("Placement drive rejected successfully.")
    return redirect(url_for("admin_drives"))   

@app.route("/admin/students") 
def admin_students():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    search_query = request.args.get("search")
    if search_query:
        if search_query.isdigit():
            students = Student.query.filter(
                (Student.full_name.ilike(f"%{search_query}%")) |
                (Student.email.ilike(f"%{search_query}%")) |
                (Student.id == int(search_query))
                ).all()
        else:
            students = Student.query.filter(
                (Student.full_name.ilike(f"%{search_query}%")) |
                (Student.email.ilike(f"%{search_query}%"))
            ).all()
    else:
        students = Student.query.all()
    return render_template("admin_students.html", students = students)

@app.route("/admin/student/<int:student_id>/deactivate")
def deactivate_student(student_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    student = Student.query.get_or_404(student_id)
    student.is_active = False
    db.session.commit()
    flash("Student deactivated successfully.")
    return redirect(url_for("admin_students"))

@app.route("/company/dashboard")
def company_dashboard():
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    company = Company.query.get_or_404(session["user_id"])
    drives = PlacementDrive.query.filter_by(company_id = company.id).all()
    return render_template("company_dashboard.html", company = company, drives = drives)

@app.route("/company/drives")
def company_drives():
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for('login'))
    company_id = session["user_id"]
    drives = PlacementDrive.query.filter_by(company_id = company_id).all()
    return render_template("company_drives.html", drives = drives)

@app.route("/company/drive/create", methods = ["GET", "POST"])
def create_drive():
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    if request.method == "POST":
        job_title = request.form.get("job_title")
        job_description = request.form.get("job_description")
        eligibility_criteria = request.form.get("eligibility_criteria")
        skills_required = request.form.get("skills_required")
        package_range = request.form.get("package_range")
        location = request.form.get("location")
        application_deadline_str = request.form.get("application_deadline")
        application_deadline = datetime.strptime(application_deadline_str, "%Y-%m-%dT%H:%M")

        new_drive = PlacementDrive(
            company_id = session["user_id"],
            job_title = job_title,
            job_description = job_description,
            eligibility_criteria = eligibility_criteria,
            skills_required = skills_required,
            package_range = package_range,
            location = location,
            application_deadline = application_deadline,
            status = "Pending"
        )
        db.session.add(new_drive)
        db.session.commit()
        flash("Placement drive created successfully and sent for admin approval.")
        return redirect(url_for("company_drives"))
    return render_template("create_drive.html")    

@app.route("/company/drive/<int:drive_id>/edit", methods = ["GET", "POST"])
def edit_drive(drive_id):
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != session["user_id"]:
        flash("You are not allowed to edit this drive.")
        return redirect(url_for("company_drives"))
    if request.method =="POST":
        drive.job_title = request.form.get("job.title")
        drive.job_description = request.form.get("job_description")
        drive.eligibility_criteria = request.form.get("eligibility_criteria")
        drive.skills_required = request.form.get("skills_required")
        drive.package_range = request.form.get("package_range")
        drive.location = request.form.get("location")
        application_deadline_str = request.form.get("application_deadline")
        drive.application_deadline = datetime.strptime(application_deadline_str, "%Y-%m-%dT%H:%M")

        drive.status = "Pending"
        db.session.commit()
        flash("Placement drive updated and sent again for admin approval.")
        return redirect(url_for("company_drives"))
    return render_template("edit_drive.html", drive = drive)

@app.route("/company/drive/<int:drive_id>/delete")
def delete_drive(drive_id):
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != session["user_id"]:
        flash("You are not allowed to delete this drive.")
        return redirect(url_for("company_drives"))
    
    db.session.delete(drive)
    db.session.commit()
    flash("Placement drive deleted successfully.")
    return redirect(url_for("company_drives"))

@app.route("/company/drive/<int:drive_id>/close")
def close_drive(drive_id):
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != session["user_id"]:
        flash("You are not allowed to close this drive.")
        return redirect(url_for("company_drives"))
    
    drive.status = "Closed"
    db.session.commit()
    flash("Placement drive closed successfully.")
    return redirect(url_for("company_drives"))

@app.route("/company/drive/<int:drive_id>/applications")
def company_drive_applications(drive_id):
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != session["user_id"]:
        flash("You are not allowed to view applications for this drive.")
        return redirect(url_for("company_drives"))
    applications = Application.query.filter_by(drive_id = drive_id).all()
    return render_template(
        "company_drive_applications.html",
        drive = drive,
        applications = applications
    )

@app.route("/company/application/<int:application_id>/status", methods = ["GET", "POST"])
def update_application_status(application_id):
    if not company_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    application = Application.query.get_or_404(application_id)
    drive = PlacementDrive.query.get_or_404(application.drive_id)

    if drive.company_id != session["user_id"]:
        flash("You are not allowed to edit this application.")
        return redirect(url_for("company_drives"))
    
    if request.method == "POST":
        new_status = request.form.get("status")
        application.status = new_status
        db.session.commit()
        flash("Application status updated successfully.")
        return redirect(url_for("company_drive_applications", drive_id = drive.id))
    return render_template(
        "update_application_status.html",
        application = application,
        drive = drive
    )    

@app.route("/student/dashboard")
def student_dashboard():
    if not student_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    return render_template("student_dashboard.html")


if __name__ == "__main__":
    app.run(debug= True)



    