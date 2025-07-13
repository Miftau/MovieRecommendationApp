import joblib
import pandas as pd
from models import db, Rating

model_data = joblib.load("model/model.pkl")
cosine_sim = model_data['cosine_sim']
movie_indices = model_data['movie_indices']
movies = model_data['movies']

def get_recommendations_for_user_db(user_id, top_n=10):
    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    high_rated = [r.movie_id for r in user_ratings if r.rating >= 4.0]

    if not high_rated:
        return []

    sim_scores = pd.Series(dtype=float)
    for movie_id in high_rated:
        idx = movie_indices.get(movie_id)
        if idx is not None:
            scores = pd.Series(cosine_sim[idx], index=movies['movieId'])
            sim_scores = sim_scores.add(scores, fill_value=0)

    sim_scores = sim_scores.drop(labels=high_rated, errors='ignore')
    top_movies = sim_scores.sort_values(ascending=False).head(top_n)
    recommendations = movies[movies['movieId'].isin(top_movies.index)]

    return recommendations[['movieId', 'title', 'genres']].to_dict(orient='records')
