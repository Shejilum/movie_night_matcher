# Movie Night Matcher 🎬

A real-time movie recommendation and matching web application built with Django and WebSockets.

## Tech Stack
- **Backend:** Django, Django Channels, Daphne (ASGI)
- **Real-Time Layer:** WebSockets
- **API Integration:** TMDB (The Movie Database)
- **Static Assets:** WhiteNoise

## Local Setup

1. **Clone the repository:**
   \\\ash
   git clone https://github.com/Shejilum/movie_night_matcher.git
   cd movie_night_matcher
   \\\

2. **Install dependencies:**
   \\\ash
   pip install -r requirements.txt
   \\\

3. **Run migrations:**
   \\\ash
   python manage.py migrate
   \\\

4. **Start the development server:**
   \\\ash
   python manage.py runserver
   \\\

Visit \http://127.0.0.1:8000\ in your browser.
