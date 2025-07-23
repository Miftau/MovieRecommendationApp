import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import os

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load the CSV with correct absolute path
#csv_path = os.path.join(BASE_DIR, "data", "movies.csv")

def train_and_save_model():
    data_path = os.path.join("data", "movies.csv")
    if not os.path.exists(data_path):
        print(f"❌ movies.csv not found at {data_path}")
        return

    # Load movie data
    movies = pd.read_csv(data_path)

    # Check movieId and genres
    if 'movieId' not in movies.columns or 'genres' not in movies.columns:
        print("❌ 'movieId' or 'genres' column missing in movies.csv")
        return

    # Clean up and fill missing
    movies['genres'] = movies['genres'].fillna("")
    movies['title'] = movies['title'].fillna("Unknown Title")
    movies['movieId'] = pd.to_numeric(movies['movieId'], errors='coerce')
    movies = movies.dropna(subset=['movieId'])  # Drop rows without movieId
    movies['movieId'] = movies['movieId'].astype(int)

    # Vectorization
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(movies['genres'])

    # Cosine similarity
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)

    # Mapping from movieId to DataFrame index
    movie_indices = pd.Series(movies.index, index=movies['movieId']).drop_duplicates()

    # Save everything
    model_data = {
        'tfidf': tfidf,
        'cosine_sim': cosine_sim,
        'movie_indices': movie_indices,
        'movies': movies
    }

    save_path = os.path.join("model", "model.pkl")
    joblib.dump(model_data, save_path)
    print(f"✅ Model trained and saved at {save_path}")

if __name__ == "__main__":
    train_and_save_model()
