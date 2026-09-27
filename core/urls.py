from django.urls import path  # pyright: ignore[reportMissingModuleSource]
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('room/<str:code>/', views.room_view, name='room_view'),
    path('room/<str:code>/more/', views.get_more_movies, name='get_more_movies'),
]