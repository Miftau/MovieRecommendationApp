import pandas as pd
import os

def convert():
    base_path = 'data/ml-100k/'

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

    # Create a genres column by combining all genre flags into strings
    genre_cols = movie_columns[5:]

    def extract_genres(row):
        return '|'.join([genre for genre in genre_cols if row[genre] == 1])

    movies['genres'] = movies.apply(extract_genres, axis=1)

    movies[['movieId', 'title', 'genres']].to_csv('data/movies.csv', index=False)
    print("✅ Created data/movies.csv")

if __name__ == "__main__":
    convert()
