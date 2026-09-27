import json
from channels.generic.websocket import AsyncWebsocketConsumer  # type: ignore[reportMissingModuleSource]
from channels.db import database_sync_to_async  # type: ignore[reportMissingModuleSource]

class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope['url_route']['kwargs']['room_code']
        self.room_group_name = f'room_{self.room_code}'

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Broadcast live member list when joining
        await self.broadcast_members()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        except Exception:
            pass

        # Broadcast updated member list when leaving
        await self.broadcast_members()

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return

        action = data.get('action')

        if action == 'join_presence':
            await self.broadcast_members()

        elif action == 'swipe_right':
            movie_id = data.get('movie_id')
            member_id = data.get('member_id')
            movie = data.get('movie')

            if not movie_id or not member_id:
                return

            is_match = await self.record_vote_and_check_match(movie_id, member_id)
            if is_match:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'match_found',
                        'movie_id': movie_id,
                        'movie': movie
                    }
                )

    async def broadcast_members(self):
        members = await self.get_members()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'members_update',
                'members': members
            }
        )

    async def members_update(self, event):
        await self.send(text_data=json.dumps({
            'event': 'MEMBERS_UPDATE',
            'members': event['members']
        }))

    async def match_found(self, event):
        await self.send(text_data=json.dumps({
            'event': 'MATCH_FOUND',
            'movie_id': event['movie_id'],
            'movie': event['movie']
        }))

    @database_sync_to_async
    def get_members(self):
        from .models import Room
        try:
            room = Room.objects.get(code=self.room_code)
            return list(room.members.values_list('user_name', flat=True).distinct())
        except Room.DoesNotExist:
            return []

    @database_sync_to_async
    def record_vote_and_check_match(self, movie_id, member_id):
        from .models import Room, SwipeVote, RoomMember
        try:
            room = Room.objects.get(code=self.room_code)
            member = RoomMember.objects.get(id=member_id)
        except (Room.DoesNotExist, RoomMember.DoesNotExist, ValueError):
            return False

        # Record or update the positive swipe
        SwipeVote.objects.update_or_create(
            room=room,
            member=member,
            tmdb_movie_id=int(movie_id),
            defaults={'liked': True}
        )

        total_members = room.members.count()
        if total_members == 0:
            return False

        likes_count = SwipeVote.objects.filter(
            room=room,
            tmdb_movie_id=int(movie_id),
            liked=True
        ).count()

        # Match occurs when all room members vote yes (supports both 1-person testing and multi-user groups)
        if likes_count >= total_members:
            if not getattr(room, 'matched_movie_id', None):
                room.matched_movie_id = int(movie_id)
                room.save(update_fields=['matched_movie_id'])
            return True

        return False