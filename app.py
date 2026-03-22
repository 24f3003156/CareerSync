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

if __name__ == "__main__":
    app.run(debug= True)