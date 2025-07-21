from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import pickle
from flask import request, jsonify
from models import db, User, Rating
from . import api_bp
import os

movies_df = pd.read_csv("data/movies.csv")

@api_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"message": "Username already exists"}), 400

    hashed = generate_password_hash(data["password"])
    new_user = User(username=data["username"], password_hash=hashed)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered"}), 201

@api_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data["username"]).first()
    if user and check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Login successful"}), 200
    return jsonify({"message": "Invalid credentials"}), 401

@api_bp.route("/movies", methods=["GET"])
def get_movies():
    movies = pd.read_csv("data/movies.csv")
    movie_list = movies[["movieId", "title", "genres"]].to_dict(orient="records")
    return jsonify(movie_list), 200


@api_bp.route("/rate", methods=["POST"])
def rate_movie():
    data = request.json
    user = User.query.filter_by(id=data["user_id"]).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    rating = Rating(
        user_id=user.id,
        movie_id=data["movie_id"],
        rating=data["rating"]
    )
    db.session.add(rating)
    db.session.commit()
    return jsonify({"message": "Rating saved"}), 201


@api_bp.route("/recommendations/<int:user_id>", methods=["GET"])
def get_recommendations(user_id):
    model_path = os.path.join("model", "model.pkl")
    if not os.path.exists(model_path):
        return jsonify({"message": "Model not found"}), 500

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    try:
        user_ratings = pd.read_sql("SELECT * FROM rating", db.engine)
        all_movies = pd.read_csv("data/movies.csv")

        # Pivot table: users x movies
        matrix = user_ratings.pivot_table(index="user_id", columns="movie_id", values="rating").fillna(0)

        if user_id not in matrix.index:
            return jsonify({"message": "No data for user"}), 404

        # Get user ratings
        user_vector = matrix.loc[user_id].values.reshape(1, -1)

        # Predict all movie scores
        scores = model.predict(user_vector)[0]
        movie_ids = matrix.columns

        top_indices = scores.argsort()[::-1][:10]
        recommended_movies = [
            {
                "movieId": int(movie_ids[i]),
                "title": all_movies[all_movies["movieId"] == int(movie_ids[i])]["title"].values[0],
                "predicted_rating": round(scores[i], 2)
            }
            for i in top_indices
        ]
        return jsonify(recommended_movies), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route("/api/movies/<int:movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    movie = movies_df[movies_df["movieId"] == movie_id]
    if movie.empty:
        return jsonify({"error": "Movie not found"}), 404

    # Query ratings from DB
    rating_stats = (
        db.session.query(
            func.avg(Rating.rating).label("avg_rating"),
            func.count(Rating.rating).label("num_ratings")
        )
        .filter(Rating.movie_id == movie_id)
        .first()
    )

    recent_ratings = (
        Rating.query.filter_by(movie_id=movie_id)
        .order_by(Rating.id.desc())
        .limit(5)
        .all()
    )


    movie_data = {"movieId": int(movie["movieId"].values[0]), "title": movie["title"].values[0],
                  "genres": movie["genres"].values[0],
                  "average_rating": round(rating_stats.avg_rating, 2) if rating_stats.avg_rating else None,
                  "total_ratings": rating_stats.num_ratings, "recent_ratings": [
            {
                "user_id": r.user_id,
                "rating": r.rating,
                "timestamp": r.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            } for r in recent_ratings
        ]}
    return jsonify(movie_data), 200
