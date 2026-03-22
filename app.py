from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Admin, Company, Student

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///placement_portal.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "secret_key"

db.init_app(app)

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
                return(redirect(url_for("index")))
            else:
                flash("Invalid admin credentials.")

        elif role == "company":
            company = Company.query.filter_by(email = email_or_username).first()
            if company and check_password_hash(company.pass_hash, password):
                session["user_id"] = company.id
                session["role"] = "company"
                flash("Company login successfull.")
                return redirect(url_for("index"))
            else:
                flash("Invalid company credentials.")

        elif role == "student":
            student = Student.query.filter_by(email = email_or_username).first()
            if student and check_password_hash(student.pass_hash, password):
                session["user_id"] = student.id
                session["role"] = "student"
                flash("Student login successfull.")
                return redirect(url_for("index"))
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
        hr_contact = request.form.get("hr_contact")
        website = request.form.get("hr_contact")
        domain = request.form.get("website")
        description = request.form.get("desciption")
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
    









if __name__ == "__main__":
    app.run(debug= True)