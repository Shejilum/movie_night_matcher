from django.db import models  # pyright: ignore[reportMissingModuleSource]

# Create your models here.

import uuid
import random
import string

def generate_room_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=6, unique=True, default=generate_room_code)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    matched_movie_id = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=20, default="all")
    provider = models.CharField(max_length=20, default="all")

    def __str__(self):
        return f"Room {self.code}"

class RoomMember(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    user_name = models.CharField(max_length=50)
    joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} ({self.room.code})"

class SwipeVote(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='votes')
    member = models.ForeignKey(RoomMember, on_delete=models.CASCADE)
    tmdb_movie_id = models.IntegerField()
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('room', 'member', 'tmdb_movie_id')
