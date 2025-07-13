import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

def train_and_save_model():
    # Load movie data
    movies = pd.read_csv("data/movies.csv")
    movies['genres'] = movies['genres'].fillna("")

    # TF-IDF vectorizer
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['genres'])

    # Cosine similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Save model components
    joblib.dump({
        'tfidf': tfidf,
        'cosine_sim': cosine_sim,
        'movie_indices': pd.Series(movies.index, index=movies['movieId']).drop_duplicates(),
        'movies': movies
    }, "model/model.pkl")

    print("✅ Model trained and saved as model/model.pkl")

if __name__ == "__main__":
    train_and_save_model()
