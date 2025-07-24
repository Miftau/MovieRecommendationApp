import pandas as pd
import os
import requests

TMDB_API_KEY = '8f0dd72bef139b88fd9ceb96f7abae3e'
BASE_PATH = 'data/ml-100k/'


def fetch_tmdb_metadata(title, year=None):
    try:
        url = 'https://api.themoviedb.org/3/search/movie'
        params = {
            'api_key': TMDB_API_KEY,
            'query': title,
            'year': year
        }
        response = requests.get(url, params=params)
        data = response.json()

        if data['results']:
            movie = data['results'][0]
            movie_id = movie['id']

            # Fetch full details using movie_id
            details_url = f"https://api.themoviedb.org/3/movie/{movie_id}"
            details = requests.get(details_url, params={'api_key': TMDB_API_KEY}).json()

            return {
                'title': details.get('title'),
                'release_date': details.get('release_date'),
                'genres': '|'.join([genre['name'] for genre in details.get('genres', [])]),
                'language': details.get('original_language'),
                'description': details.get('overview'),
                'poster_path': f"https://image.tmdb.org/t/p/w500{details['poster_path']}" if details.get('poster_path') else '',
                'tagline': details.get('tagline', ''),
                'runtime': details.get('runtime'),
                'rating': details.get('vote_average'),
                'vote_count': details.get('vote_count')
            }
    except Exception as e:
        print(f"❌ Error fetching metadata for '{title}': {e}")
    return {
        'title': title,
        'release_date': None,
        'genres': '',
        'language': '',
        'description': '',
        'poster_path': '',
        'tagline': '',
        'runtime': None,
        'rating': None,
        'vote_count': None
    }


def parse_title_and_year(title):
    if title.endswith(')'):
        try:
            name = title[:-7]
            year = title[-5:-1]
            return name.strip(), year.strip()
        except:
            return title, None
    return title, None


def convert():
    os.makedirs('data', exist_ok=True)

    print("🔄 Reading movie data...")
    movie_columns = [
        'movieId', 'title', 'release_date', 'video_release_date', 'imdb_url',
        'unknown', 'Action', 'Adventure', 'Animation', "Children's", 'Comedy',
        'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror',
        'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
    ]

    movies_df = pd.read_csv(
        os.path.join(BASE_PATH, 'u.item'),
        sep='|',
        names=movie_columns,
        encoding='latin-1'
    )

    enriched_data = []

    for i, row in movies_df.iterrows():
        title, year = parse_title_and_year(row['title'])
        metadata = fetch_tmdb_metadata(title, year)
        metadata['movieId'] = row['movieId']
        enriched_data.append(metadata)

        print(f"✅ {i+1}/{len(movies_df)} - {title} ({year}) enriched.")

    df = pd.DataFrame(enriched_data)
    df.to_csv('data/movies.csv', index=False)
    print("✅ All movies saved to data/movies.csv")


if __name__ == '__main__':
    convert()
