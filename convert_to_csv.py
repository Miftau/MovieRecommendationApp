import pandas as pd
import os
import requests


TMDB_API_KEY = '8f0dd72bef139b88fd9ceb96f7abae3e'
BASE_PATH = 'data/ml-100k/'


def fetch_tmdb_metadata(title, year=None):
    if not TMDB_API_KEY:
        return {}

    try:
        query = f"{title} ({year})" if year else title
        url = f"https://api.themoviedb.org/3/search/movie"
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data['results']:
            movie = data['results'][0]
            return {
                'description': movie.get('overview', ''),
                'poster': f"https://image.tmdb.org/t/p/w500{movie['poster_path']}" if movie.get('poster_path') else '',
                'year': movie.get('release_date', '')[:4] if movie.get('release_date') else '',
                'language': movie.get('original_language', '')
            }
        return {}
    except Exception as e:
        print(f"Error fetching metadata for {title}: {e}")
        return {}


def convert():
    os.makedirs('data', exist_ok=True)

    # Convert u.data to ratings.csv
    ratings = pd.read_csv(
        os.path.join(BASE_PATH, 'u.data'),
        sep='\t',
        names=['userId', 'movieId', 'rating', 'timestamp'],
        engine='python'
    )
    ratings.to_csv('data/ratings.csv', index=False)
    print("✅ Created data/ratings.csv")

    # Convert u.item to movies_extended.csv
    movie_columns = [
        'movieId', 'title', 'release_date', 'video_release_date', 'imdb_url',
        'unknown', 'Action', 'Adventure', 'Animation', 'Children\'s', 'Comedy', 'Crime',
        'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical',
        'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]

    movies = pd.read_csv(
        os.path.join(BASE_PATH, 'u.item'),
        sep='|',
        names=movie_columns,
        encoding='latin-1',
        engine='python'
    )

    # Create genres column
    genre_cols = movie_columns[5:]

    def extract_genres(row):
        return '|'.join([genre for genre in genre_cols if row[genre] == 1])

    movies['genres'] = movies.apply(extract_genres, axis=1)

    # Extract year from release_date
    movies['year'] = movies['release_date'].str[-4:]

    # Add placeholders for additional metadata
    movies['description'] = ''
    movies['poster'] = ''
    movies['language'] = ''

    # Optional: limit how many movies to enrich (e.g., first 100)
    for i, row in movies.iterrows():
        metadata = fetch_tmdb_metadata(row['title'], row['year'])
        for key in metadata:
            movies.at[i, key] = metadata[key]
        if i % 10 == 0:
            print(f"Processed {i} movies...")

    # Save final CSV
    movies[['movieId', 'title', 'genres', 'year', 'description', 'poster', 'language']].to_csv(
        'data/movies.csv', index=False
    )
    print("✅ Created data/movies_extended.csv")


if __name__ == "__main__":
    convert()
