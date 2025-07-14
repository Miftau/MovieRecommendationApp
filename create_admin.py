import os
from flask import Flask
from models import db, Admin
from werkzeug.security import generate_password_hash
import sqlite3

# Absolute path to db
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
os.makedirs(os.path.join(BASE_DIR, 'data'), exist_ok=True)
db_path = os.path.join(BASE_DIR, 'data', 'app.db')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    existing_admin = Admin.query.filter_by(username=username).first()
    if existing_admin:
        print("❌ Admin already exists.")
    else:
        new_admin = Admin(username=username, password_hash=generate_password_hash(password))
        db.session.add(new_admin)
        db.session.commit()
        print("✅ Admin created successfully.")

