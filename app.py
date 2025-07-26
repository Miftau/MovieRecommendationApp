from flask import Flask
from config import Config
from models import db
from admin.routes import admin_bp
from api.routes import api_bp
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
import requests

app = Flask(__name__)

PING_URL = "https://movierecommender-i9ne.onrender.com/"
def keep_alive():
    try:
        response = requests.get(PING_URL)
        print(f"[Keep Alive] Status: {response.status_code}")
    except Exception as e:
        print(f"[Keep Alive] Failed: {e}")

# Schedule the job every 10 minutes
scheduler = BackgroundScheduler()
scheduler.add_job(func=keep_alive, trigger="interval", minutes=10)
scheduler.start()

# Shut down scheduler when exiting the app
import atexit
atexit.register(lambda: scheduler.shutdown())

CORS(app)
app.config.from_object(Config)

db.init_app(app)
app.register_blueprint(admin_bp)
app.register_blueprint(api_bp, url_prefix="/api")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run()


