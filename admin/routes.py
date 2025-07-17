from flask import render_template, request, redirect, session
from werkzeug.security import check_password_hash
from models import db, User, Rating, Admin
from . import admin_bp
import pandas as pd
from sqlalchemy import func

@admin_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        admin = Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password_hash, password):
            session["admin"] = admin.username
            return redirect("/dashboard")
        return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@admin_bp.route("/dashboard")
def dashboard():
    if not session.get("admin"):
        return redirect("/")
    user_count = User.query.count()
    rating_count = Rating.query.count()

    top_rated_movies = (
        db.session.query(Rating.movie_id, func.avg(Rating.rating).label("avg_rating"))
        .group_by(Rating.movie_id)
        .order_by(func.avg(Rating.rating).desc())
        .limit(5)
        .all()
    )

    movies_df = pd.read_csv("data/movies.csv")
    top_movies = [
        {
            "title": movies_df[movies_df["movieId"] == m_id]["title"].values[0],
            "rating": round(avg, 2)
        }
        for m_id, avg in top_rated_movies
    ]

    return render_template("dashboard.html", users=user_count, ratings=rating_count, top_movies=top_movies)

@admin_bp.route("/users")
def users():
    if not session.get("admin"):
        return redirect("/")
    users = User.query.all()
    return render_template("users.html", users=users)

@admin_bp.route("/ratings")
def ratings():
    if not session.get("admin"):
        return redirect("/")
    ratings = Rating.query.all()
    return render_template("ratings.html", ratings=ratings)

@admin_bp.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")
