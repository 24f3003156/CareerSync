from app import app
from models import db, Admin
from werkzeug.security import generate_password_hash

def create_db():
    with app.app_context():
        db.create_all()

        existing_admin = Admin.query.filter_by(username ="admin").first()

        if existing_admin is None:
            admin = Admin(username = "admin", pass_hash= generate_password_hash("CareerSyncAdmin"), f_name = "CareerSync", l_name = "Admin")
            db.session.add(admin)
            db.session.commit()
            print("Database created and Admin inserted")

        else:
            print("Database exists and Admin already present.")

if __name__ == "__main__":
    create_db()