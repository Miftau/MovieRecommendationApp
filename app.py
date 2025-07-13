from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from model.recommender import get_recommendations_for_user_db
from models import db, User, Rating

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data/app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)



# --- INIT DB ---
@app.before_request
def create_tables():
    db.init_app(app)
    with app.app_context():
        db.create_all()


# --- AUTH ---

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Username already exists"}), 400
    hashed_password = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User registered successfully"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401
    token = create_access_token(identity=user.id)
    return jsonify(access_token=token), 200

# --- MOVIES ---

@app.route("/movies", methods=["GET"])
@jwt_required()
def list_movies():
    movies = pd.read_csv("data/movies.csv")
    return jsonify(movies[['movieId', 'title', 'genres']].to_dict(orient='records'))

# --- RATINGS ---

@app.route("/rate", methods=["POST"])
@jwt_required()
def rate_movie():
    data = request.get_json()
    user_id = get_jwt_identity()

    rating = Rating(
        user_id=user_id,
        movie_id=data["movieId"],
        rating=data["rating"]
    )
    db.session.add(rating)
    db.session.commit()

    return jsonify({"msg": "Rating submitted!"}), 200

# --- RECOMMENDATIONS ---

@app.route("/recommendations", methods=["GET"])
@jwt_required()
def recommendations():
    user_id = get_jwt_identity()
    recs = get_recommendations_for_user_db(user_id)
    return jsonify(recs)

# --- MAIN ---
if __name__ == "__main__":
    app.run(debug=True)

