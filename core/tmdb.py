import os
import random
import requests

TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "4ccdac6b67c4eb3ba72a0480394fed30")
BASE_URL = "https://api.themoviedb.org/3"

FALLBACK_MOVIES = [
    {
        "id": 157336,
        "title": "Interstellar",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.",
        "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "release_date": "2014-11-05",
        "vote_average": 8.4,
        "providers": ["Prime Video"],
    },
    {
        "id": 27205,
        "title": "Inception",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life.",
        "poster_path": "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "release_date": "2010-07-15",
        "vote_average": 8.4,
        "providers": ["Netflix"],
    },
    {
        "id": 550,
        "title": "Fight Club",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
        "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "release_date": "1999-10-15",
        "vote_average": 8.4,
        "providers": ["Netflix", "Prime Video"],
    },
    {
        "id": 155,
        "title": "The Dark Knight",
        "overview": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent against the Joker.",
        "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "release_date": "2008-07-16",
        "vote_average": 8.5,
        "providers": ["Netflix"],
    },
    {
        "id": 12,
        "title": "Finding Nemo",
        "overview": "Nemo, an adventurous young clownfish, is unexpectedly taken from his Great Barrier Reef home to a dentist's office aquarium.",
        "poster_path": "/ggQ6nvl421xM0zX7n6q6f4a8b8Q.jpg",
        "release_date": "2003-05-30",
        "vote_average": 7.8,
        "providers": ["Disney+"],
    },
    {
        "id": 299536,
        "title": "Avengers: Infinity War",
        "overview": "As the Avengers and their allies have continued to protect the world from threats too large for any one hero to handle, a new danger has emerged from the cosmic shadows: Thanos.",
        "poster_path": "/7WsyChQLEftFiDOVTGkv3hFpyyt.jpg",
        "release_date": "2018-04-25",
        "vote_average": 8.3,
        "providers": ["Disney+"],
    },
    {
        "id": 19995,
        "title": "Avatar",
        "overview": "In the 22nd century, a paraplegic Marine is dispatched to the moon Pandora on a unique mission, but becomes torn between following orders and protecting an alien civilization.",
        "poster_path": "/kyeqWdyUXW608qlYkRqosgbbJyK.jpg",
        "release_date": "2009-12-15",
        "vote_average": 7.6,
        "providers": ["Disney+"],
    }
]

def get_popular_movies(region="IN", genre="all", provider="all", page=None):
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        return FALLBACK_MOVIES

    fetch_page = page if page is not None else 1

    url = f"{BASE_URL}/discover/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "popularity.desc",
        "include_adult": "false",
        "include_video": "false",
        "page": fetch_page,
    }

    if genre and str(genre).lower() != "all":
        params["with_genres"] = str(genre)

    if provider and str(provider).lower() != "all":
        params["watch_region"] = region
        params["with_watch_providers"] = str(provider)
        params["with_watch_monetization_types"] = "flatrate|free|ads"

    try:
        # (connect timeout=1.5s, read timeout=2.5s) so page never hangs
        response = requests.get(url, params=params, timeout=(1.5, 2.5))
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            if results:
                if fetch_page == 1:
                    random.shuffle(results)
                
                seen_ids = set()
                movies = []
                for item in results:
                    movie_id = item.get("id")
                    poster_path = item.get("poster_path")
                    if movie_id and movie_id not in seen_ids and poster_path:
                        seen_ids.add(movie_id)
                        movies.append({
                            "id": movie_id,
                            "title": item.get("title") or "Unknown Title",
                            "overview": item.get("overview") or "No description available.",
                            "poster_path": poster_path,
                            "release_date": item.get("release_date", "2024-01-01"),
                            "vote_average": item.get("vote_average", 0.0),
                            "providers": ["Streaming Available"],
                        })
                if movies:
                    return movies[:15]

        return FALLBACK_MOVIES

    except Exception:
        # Fall back instantly on connection/DNS timeouts
        return FALLBACK_MOVIES