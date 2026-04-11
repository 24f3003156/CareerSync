import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session 
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Company, Student, PlacementDrive, Application, Placement

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "career_sync_secret"
app.config["UPLOAD_FOLDER"] = "static/uploads/resumes"
app.config["ALLOWED_EXTENSIONS"] = {"pdf"}

db.init_app(app)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".",1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

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
        internship_experience = request.form.get("internship_experience")
        co_curricular_achievements = request.form.get("co_curricular_achievements")

        resume = request.files.get("resume")

        if not resume or resume.filename == "":
            flash("Resume file is required.")
            return redirect(url_for("register_student"))
        
        if not allowed_file(resume.filename):
            flash("Only PDF resume files are allowed.")
            return redirect(url_for("register_student"))
        
        resume_filename = secure_filename(resume.filename)        
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_filename)
        resume.save(resume_path)

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

@app.route("/admin/change-password", methods = ["GET", "POST"])
def admin_change_password():
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    admin = Admin.query.get_or_404(session["user_id"])

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not current_password or not new_password or not confirm_password:
            flash("All fields are required.")
            return redirect(url_for("admin_change_password"))
        
        if not check_password_hash(admin.pass_hash, current_password):
            flash("Current password is incorrect.")
            return redirect(url_for("admin_change_password"))
        
        if new_password != confirm_password:
            flash("New password and confirm password do not match.")
            return redirect(url_for("admin_change_password"))

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

@app.route("/admin/company/<int:company_id>/delete")
def delete_company(company_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    company = Company.query.get_or_404(company_id)
    existing_drives = PlacementDrive.query.filter_by(company_id = company.id).first()
    if existing_drives:
        flash("Company cannot be deleted because it has placement drives.")
        return redirect(url_for("admin_companies"))
    db.session.delete(company)
    db.session.commit()
    flash("Company deleted successfully.")
    return redirect(url_for("admin_companies"))

@app.route("/admin/company/<int:company_id>/reset-password", methods = ["GET", "POST"])
def reset_company_password(company_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    company = Company.query.get_or_404(company_id)

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            flash("All fields are required.")
            return redirect(url_for("reset_company_password", company_id = company.id))
        
        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("reset_company_password", company_id = company.id))
        
        company.pass_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Company password reset successfully.")
        return redirect(url_for("admin_companies"))
    return render_template("reset_company_password.html", company= company)
    
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

@app.route("/admin/student/<int:student_id>/activate")
def activate_student(student_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    student = Student.query.get_or_404(student_id)
    student.is_active = True
    db.session.commit()
    flash("Student activated successfully.")
    return redirect(url_for("admin_students"))

@app.route("/admin/student/<int:student_id>/reset-password", methods = ["GET", "POST"])
def reset_student_password(student_id):
    if not admin_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    student = Student.query.get_or_404(student_id)

    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        if not new_password or not confirm_password:
            flash("All fields are required.")
            return redirect(url_for("reset_student_password", student_id = student.id))
        
        if new_password != confirm_password:
            flash("Passwords do not match.")
            return redirect(url_for("reset_student_password", student_id = student_id))
        
        student.pass_hash = generate_password_hash(new_password)
        db.session.commit()

        flash("Student password reset successfully.")
        return redirect(url_for("admin_students"))
    return render_template("reset_student_password.html", student = student)

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
        allowed_cgpa_values = ["6.0", "6.5", "7.0", "7.5", "8.0", "8.5", "9.0"]
        if eligibility_criteria not in allowed_cgpa_values:
            flash("Please select a valid minimum CGPA.")
            return redirect(url_for("create_drive"))
        
        skills_required = request.form.get("skills_required")
        package_range = request.form.get("package_range")
        if package_range:
            try:
                package_range = float(package_range)
            except:
                flash("Package range must be a number.")
                return redirect(url_for("create_drive"))
        location = request.form.get("location")
        application_deadline_str = request.form.get("application_deadline")        

        if not job_title or not job_description or not eligibility_criteria or not skills_required or not location or not application_deadline_str:
            flash("All required fields must be filled.")
            return redirect(url_for("create_drive"))
        try:
            application_deadline = datetime.strptime(application_deadline_str, "%Y-%m-%dT%H:%M")
        except:
            flash("Invalid deadline format.")
            return redirect(url_for("create_drive"))
        
        if application_deadline < datetime.now():
            flash("Deadline cannot be in the past.")
            return redirect(url_for("create_drive"))

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
    return render_template("create_drive.html", now = datetime.now().strftime("%Y-%m-%dT%H:%M"))    

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
        drive.job_title = request.form.get("job_title")
        drive.job_description = request.form.get("job_description")

        eligibility_criteria = request.form.get("eligibility_criteria")
        allowed_cgpa_values = ["6.0", "6.5", "7.0", "7.5", "8.0", "8.5", "9.0"]
        if eligibility_criteria not in allowed_cgpa_values:
            flash("Please select a valid minimum CGPA.")
            return redirect(url_for("edit_drive", drive_id = drive_id))
        drive.eligibility_criteria = eligibility_criteria        

        drive.skills_required = request.form.get("skills_required")
        package_range = request.form.get("package_range")
        if package_range:
            try:
                drive.package_range = float(package_range)
            except:
                flash("Package range must be a number.")
                return redirect(url_for("edit_drive", drive_id = drive_id))
        else:
            drive.package_range = None

        drive.location = request.form.get("location")

        application_deadline_str = request.form.get("application_deadline")
        if not application_deadline_str:
            flash("Application deadline is required.")
            return redirect(url_for("edit_drive", drive_id = drive_id))
        try:
            application_deadline = datetime.strptime(application_deadline_str, "%Y-%m-%dT%H:%M")
        except:
            flash("Invalid deadline format.")
            return redirect(url_for("edit_drive", drive_id = drive_id))
        
        if application_deadline < datetime.now():
            flash("Deadline cannot be in the past.")
            return redirect(url_for("edit_drive", drive_id = drive_id))
        
        drive.application_deadline = application_deadline

        drive.status = "Pending"
        db.session.commit()
        flash("Placement drive updated and sent again for admin approval.")
        return redirect(url_for("company_drives"))
    return render_template(
        "edit_drive.html",
          drive = drive,
          now = datetime.now().strftime("%Y-%m-%dT%H:%M"))

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
        allowed_status = ["Shortlisted", "Selected", "Rejected", "Interview", "Placed"]
        if new_status not in allowed_status:
            flash("Invalid status selected.")
            return redirect(url_for("company_drive_applications", drive_id = drive.id))
        application.status = new_status

        if new_status == "Placed":
            existing_placement = Placement.query.filter_by(
                student_id = application.student_id,
                drive_id = application.drive_id
            ).first()

            if not existing_placement:
                new_placement = Placement(
                    student_id = application.student_id,
                    drive_id = application.drive_id,
                    company_id = drive.company_id,
                    final_status = "Placed",
                    top_50_packages = 0
                )
                db.session.add(new_placement)
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
    student = Student.query.get_or_404(session["user_id"])
    applications = Application.query.filter_by(student_id = student.id).all()    
    return render_template(
        "student_dashboard.html",
        student = student,
        applications = applications)

@app.route("/student/drives")
def student_drives():
    if not student_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))

    search_query = request.args.get("search")
    current_time = datetime.now()
    
    if search_query:
        drives = PlacementDrive.query.filter(
           (PlacementDrive.status =="Approved")&
           (PlacementDrive.application_deadline >= current_time) &
        (
            PlacementDrive.job_title.ilike(f"%{search_query}%") |
            PlacementDrive.skills_required.ilike(f"%{search_query}%") |
            PlacementDrive.location.ilike(f"%{search_query}%")
        )
    ).all()
    else:
        drives = PlacementDrive.query.filter(
            (PlacementDrive.status =="Approved") &
            (PlacementDrive.application_deadline >= current_time) 
        ).all()     
              
    return render_template("student_drives.html", drives = drives)

@app.route("/student/drive/<int:drive_id>/apply")
def apply_drive(drive_id):
    if not student_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    student_id = session["user_id"]

    drive = PlacementDrive.query.get_or_404(drive_id)
    company = Company.query.get_or_404(drive.company_id)

    if drive.status != "Approved":
        flash("You can apply to approved ones only.")
        return redirect(url_for("student_drives"))
    
    if company.approval_status != "Approved" or company.is_active ==False:
        flash("You cannot apply to this drive.")
        return redirect(url_for("student_drives"))
    
    existing_application = Application.query.filter_by(
        student_id = student_id,
        drive_id = drive.id
    ).first()

    if existing_application:
        flash("You have already applied for this drive.")
        return redirect(url_for("student_drives"))
    
    new_application = Application(
        student_id = student_id,
        drive_id = drive.id,
        status = "Applied"
    )
    db.session.add(new_application)
    db.session.commit()
    flash("Application submitted successfully.")
    return redirect(url_for("student_drives"))
    
@app.route("/student/applications")
def student_applications():
    if not student_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    student_id = session["user_id"]
    applications = Application.query.filter_by(student_id = student_id).all()

    return render_template("student_applications.html", applications = applications)

@app.route("/student/history")
def student_history():
    if not student_logged_in():
        flash("Unauthorized access.")
        return redirect(url_for("login"))
    
    student_id = session["user_id"]
    placements = Placement.query.filter_by(student_id = student_id).all()

    return render_template("student_history.html", placements = placements)

if __name__ == "__main__":
    app.run(debug= True)



    