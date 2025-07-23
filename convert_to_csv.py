import pandas as pd
import os
import requests
import time

TMDB_API_KEY = '8f0dd72bef139b88fd9ceb96f7abae3e'
BASE_PATH = 'data/ml-100k/'
TMDB_SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
TMDB_MOVIE_DETAILS_URL = "https://api.themoviedb.org/3/movie/"


def fetch_tmdb_metadata(title, year=None):
    try:
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year
        }
        response = requests.get(TMDB_SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("results"):
            return {}

        movie = data["results"][0]
        movie_id = movie.get("id")

        # Fetch full details
        details_response = requests.get(f"{TMDB_MOVIE_DETAILS_URL}{movie_id}", params={'api_key': TMDB_API_KEY})
        details_response.raise_for_status()
        details = details_response.json()

        return {
            'overview': details.get('overview', ''),
            'poster_path': f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get(
                'poster_path') else '',
            'release_date': details.get('release_date', ''),
            'runtime': details.get('runtime', ''),
            'tagline': details.get('tagline', ''),
            'rating': details.get('vote_average', ''),
            'vote_count': details.get('vote_count', ''),
            'language': details.get('original_language', '')
        }

    except Exception as e:
        print(f"❌ Error fetching TMDB metadata for '{title}': {e}")
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

    # Convert u.item to movies.csv with enrichment
    movie_columns = [
        'movieId', 'title', 'release_date', 'video_release_date', 'imdb_url',
        'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime',
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
    movies['genres'] = movies[genre_cols].apply(lambda row: '|'.join([g for g in genre_cols if row[g] == 1]), axis=1)
    movies['year'] = movies['release_date'].str[-4:]

    # Add columns to hold TMDB metadata
    metadata_columns = ['overview', 'poster_path', 'release_date', 'runtime', 'tagline', 'rating', 'vote_count',
                        'language']
    for col in metadata_columns:
        movies[col] = ''

    # Fetch metadata from TMDB for all movies
    for i, row in movies.iterrows():
        title = row['title']
        year = row['year']

        metadata = fetch_tmdb_metadata(title, year)
        for key in metadata:
            movies.at[i, key] = metadata[key]

        print(f"✅ [{i + 1}/{len(movies)}] Enriched: {title}")
        time.sleep(0.25)  # Add slight delay to avoid rate limits

    # Final export
    output_cols = ['movieId', 'title', 'genres', 'overview', 'release_date', 'runtime', 'tagline', 'rating',
                   'vote_count', 'poster_path', 'language']
    movies[output_cols].to_csv('data/movies.csv', index=False)
    print("🎉 All movies enriched and saved to data/movies.csv")


if __name__ == "__main__":
    convert()
