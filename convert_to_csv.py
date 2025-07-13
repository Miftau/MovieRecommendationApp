import pandas as pd
import os

def convert():
    base_path = 'MovieRecommendationApp/data/ml-100k/'

    # Convert u.data to ratings.csv
    ratings = pd.read_csv(
        os.path.join(base_path, 'u.data'),
        sep='\t',
        names=['userId', 'movieId', 'rating', 'timestamp'],
        engine='python'
    )
    ratings.to_csv('data/ratings.csv', index=False)
    print("✅ Created data/ratings.csv")

    # Convert u.item to movies.csv
    # Columns: movieId | title | release date | video release | IMDb URL | genres...
    movie_columns = [
        'movieId', 'title', 'release_date', 'video_release_date', 'imdb_url',
        'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime',
        'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
        'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]

    movies = pd.read_csv(
        os.path.join(base_path, 'u.item'),
        sep='|',
        names=movie_columns,
        encoding='latin-1',
        engine='python'
    )

    # Optional: Combine genres into a single string for each movie
    genre_cols = movie_columns[5:]
    movies['genres'] = movies[genre_cols].dot(pd.Series(genre_cols + ' ')).str.strip()

    movies[['movieId', 'title', 'genres']].to_csv('data/movies.csv', index=False)
    print("✅ Created data/movies.csv")

if __name__ == "__main__":
    convert()
