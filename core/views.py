import json
from django.shortcuts import render, redirect, get_object_or_404  # type: ignore[reportMissingModuleSource]
from django.http import JsonResponse  # type: ignore[reportMissingModuleSource]
from .models import Room, RoomMember
from .tmdb import get_popular_movies

# Reliable fallback catalog to guarantee cards render even without an API key
DEFAULT_FALLBACK_MOVIES = [
    {
        "id": 157336,
        "title": "Interstellar",
        "overview": "The adventures of a group of explorers who make use of a newly discovered wormhole to surpass the limitations on human space travel.",
        "poster_path": "/gEU2QniE6E77NI6lCU6MxlNBvIx.jpg",
        "vote_average": 8.4,
        "release_date": "2014-11-05",
        "providers": ["Prime Video"]
    },
    {
        "id": 27205,
        "title": "Inception",
        "overview": "Cobb, a skilled thief who commits corporate espionage by infiltrating the subconscious of his targets is offered a chance to regain his old life.",
        "poster_path": "/oYuLEt3zVCKq57qu2F8dT7NIa6f.jpg",
        "vote_average": 8.4,
        "release_date": "2010-07-15",
        "providers": ["Netflix"]
    },
    {
        "id": 550,
        "title": "Fight Club",
        "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
        "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "vote_average": 8.4,
        "release_date": "1999-10-15",
        "providers": ["Netflix", "Prime Video"]
    },
    {
        "id": 155,
        "title": "The Dark Knight",
        "overview": "Batman raises the stakes in his war on crime with the help of Lt. Jim Gordon and District Attorney Harvey Dent against the Joker.",
        "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
        "vote_average": 8.5,
        "release_date": "2008-07-16",
        "providers": ["Netflix"]
    },
    {
        "id": 12,
        "title": "Finding Nemo",
        "overview": "Nemo, an adventurous young clownfish, is unexpectedly taken from his Great Barrier Reef home to a dentist's office aquarium.",
        "poster_path": "/ggQ6nvl421xM0zX7n6q6f4a8b8Q.jpg",
        "vote_average": 7.8,
        "release_date": "2003-05-30",
        "providers": ["Disney+"]
    }
]

def home(request):
    if request.method == "POST":
        action = request.POST.get("action")
        user_name = request.POST.get("user_name", "Anonymous").strip() or "Anonymous"

        if action == "create":
            genre = request.POST.get("genre", "all")
            provider = request.POST.get("provider", "all")
            
            room = Room.objects.create(genre=genre, provider=provider)
            member, _ = RoomMember.objects.get_or_create(room=room, user_name=user_name)
            request.session['member_id'] = str(member.id)
            return redirect('room_view', code=room.code)

        elif action == "join":
            code = request.POST.get("code", "").strip().upper()
            room = get_object_or_404(Room, code=code)
            member, _ = RoomMember.objects.get_or_create(room=room, user_name=user_name)
            request.session['member_id'] = str(member.id)
            return redirect('room_view', code=room.code)

    return render(request, "index.html")

def room_view(request, code):
    room = get_object_or_404(Room, code=code)
    member_id = request.session.get('member_id')
    
    # If session expired or opening a copied link in a new incognito window, create member
    if not member_id:
        member = RoomMember.objects.create(room=room, user_name="Guest")
        request.session['member_id'] = str(member.id)
    else:
        member = RoomMember.objects.filter(id=member_id, room=room).first()
        if not member:
            member = RoomMember.objects.create(room=room, user_name="Guest")
            request.session['member_id'] = str(member.id)

    # Attempt fetch; fallback to default list if TMDB yields no movies
    try:
        movies = get_popular_movies(genre=room.genre, provider=room.provider)
    except Exception as e:
        print(f"TMDB Fetch Exception: {e}")
        movies = []

    if not movies:
        movies = DEFAULT_FALLBACK_MOVIES

    return render(request, "room.html", {
        "room": room,
        "member": member,
        "movies_json": json.dumps(movies)
    })

def get_more_movies(request, code):
    room = get_object_or_404(Room, code=code)
    page = int(request.GET.get('page', 2))
    try:
        movies = get_popular_movies(genre=room.genre, provider=room.provider, page=page)
    except Exception:
        movies = []
    return JsonResponse({'movies': movies})