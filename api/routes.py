from sqlalchemy import func
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from flask import request, jsonify
from models import db, User, Rating
import os
from flask import Blueprint

api_bp = Blueprint('api', __name__)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))



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
    try:
        # Load all ratings from DB
        ratings_df = pd.read_sql("SELECT * FROM rating", db.engine)

        if user_id not in ratings_df['user_id'].unique():
            return jsonify({"message": "No ratings found for user"}), 404

        # Create user-item matrix
        user_item_matrix = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating')

        # Get target user's ratings
        target_user_ratings = user_item_matrix.loc[user_id].dropna()

        # Compute similarity with other users
        similarities = user_item_matrix.corrwith(target_user_ratings, axis=1, drop=True).dropna()

        # Drop similarity with self
        similarities = similarities.drop(user_id, errors='ignore')

        # Get top N similar users
        similar_users = similarities.sort_values(ascending=False).head(5).index

        # Aggregate ratings from similar users
        similar_users_ratings = user_item_matrix.loc[similar_users]

        # Weighted average of ratings for each movie
        avg_ratings = similar_users_ratings.mean().dropna()

        # Exclude movies the user has already rated
        unrated_movies = avg_ratings[~avg_ratings.index.isin(target_user_ratings.index)]

        # Top 10 recommendations
        top_movies = unrated_movies.sort_values(ascending=False).head(10)

        # Load movie titles
        movies_df = pd.read_csv("data/movies.csv")
        movies_df.set_index("movieId", inplace=True)

        recommendations = [
            {
                "movieId": int(movie_id),
                "title": movies_df.loc[movie_id]["title"],
                "predicted_rating": round(score, 2)
            }
            for movie_id, score in top_movies.items()
            if movie_id in movies_df.index
        ]

        return jsonify(recommendations), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@api_bp.route("/movies/<int:movie_id>", methods=["GET"])
def get_movie_details(movie_id):
    try:
        # Load enriched movie data
        movies_df = pd.read_csv("data/movies.csv")
        movie = movies_df[movies_df['movieId'] == movie_id]

        if movie.empty:
            return jsonify({"message": "Movie not found"}), 404

        movie = movie.iloc[0]

        return jsonify({
            "movieId": int(movie['movieId']),
            "title": movie['title'],
            "genres": movie['genres'],
            "language": movie['language'],
            "description": movie.get('overview', 'Not available'),
            "release_date": movie.get('release_date', 'Not available'),
            "runtime": movie.get('runtime', 'Not available'),
            "tagline": movie.get('tagline', 'Not available'),
            "rating": movie.get('rating', 'Not available'),
            "vote_count": movie.get('vote_count', 'Not available'),
            "poster_path": movie.get('poster_path', '')
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500