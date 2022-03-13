from django.shortcuts import render, redirect
from .credentials import REDIRECT_URI, CLIENT_SECRET, CLIENT_ID
from rest_framework.views import APIView
from requests import Request, post
from rest_framework import status
from rest_framework.response import Response
from .util import * 
from api.models import Room
from .models import Vote

#Returns URL to authenticate spotify application 
class AuthURL(APIView):
    def get(self, request, fornat=None):
        # info we want to access in the app (need to add more scopes later)
        # find more scopes @ developer.spotify.com
        # https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing'

        # URL to authorize account
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scopes,
            'response_type': 'code',    #Requesting the code to authenticate user
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID
        }).prepare().url   #have front end get url 

        return Response({'url': url}, status=status.HTTP_200_OK)

#Send request to get access to all the tokens and send to the frontend 
def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    #create database to store all of the tokens and refresh tokens (new session needs new tokens and etc )

    #Check if there is a session key, if not, create 
    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(
        request.session.session_key, access_token, token_type, expires_in, refresh_token)

    return redirect('frontend:')  #put in name of application (frontend:) after : put page to go to 

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        return Response({'status': is_authenticated}, status=status.HTTP_200_OK)

#Get current info about current song and return to Frontend 
class CurrentSong(APIView):
    def get(self, request, format=None):
        room_code = self.request.session.get('room_code') #Get room user is in 

        # Get access to room object to find out who host is 
        # because who is requesting info about song might not be the host 
        # if someone sends the request who isnt the host, need to find room, and host to get the info 
        room = Room.objects.filter(code=room_code)
        
        # Everytime there is a request sent to current song, update the room with the current song id 
        if room.exists():
            room = room[0]
        else:
            return Response({}, status=status.HTTP_404_NOT_FOUND)
        host = room.host
        endpoint = "player/currently-playing"
        response = execute_spotify_api_request(host, endpoint)

        if 'error' in response or 'item' not in response:
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')
        artist_string = "" #Handles if there are multiple artists for a song, cleans up for frontend 

        for i, artist in enumerate(item.get('artists')):
            if i > 0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name

        # Number of votes for current song in room
        votes = len(Vote.objects.filter(room=room, song_id=room.current_song))

        song = {
            'title': item.get('name'),
            'artist': artist_string,
            'duration': duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing': is_playing,
            'votes': votes,     #Current votes to skip the song 
            'votes_required': room.votes_to_skip, #Constantly check number of votes room requires to skip a song 
            'id': song_id
        }

        # Check if the song changed and update the room/objects 
        self.update_room_song(room, song_id)

        return Response(song, status=status.HTTP_200_OK)
    
    # Everytime there is a request sent to current song, update the room with the current song_id 
    def update_room_song(self, room, song_id):
        current_song = room.current_song

        #Check before performing update, make sure were not updating the same thing 
        # If song has changed, update the current_song in the room 
        if current_song != song_id:
            room.current_song = song_id
            room.save(update_fields=['current_song'])

            #Delete all the vote objects for this room when the song changes 
            votes = Vote.objects.filter(room=room).delete()

    

class PauseSong(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)


class PlaySong(APIView):
    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key == room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({}, status=status.HTTP_403_FORBIDDEN)

class SkipSong(APIView):
    # Someone is requesting to skip the current song 
    def post(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]

        #if someone is voting and they are not the host, create a new vote for them 
        votes = Vote.objects.filter(room=room, song_id=room.current_song)

        #Check how many votes we need to be able to skip the song 
        votes_needed = room.votes_to_skip

        #If you are the room host, skip song 
        #If you are a guest, skip current song if number of Votes is greater than votes needed
        if self.request.session.session_key == room.host or len(votes) + 1 >= votes_needed:
            #Before we skip current song, delete votes 
            votes.delete()
            #Skip song 
            skip_song(room.host)
        else:
            vote = Vote(user=self.request.session.session_key, room=room, song_id=room.current_song)
            vote.save()

        return Response({}, status.HTTP_204_NO_CONTENT)


