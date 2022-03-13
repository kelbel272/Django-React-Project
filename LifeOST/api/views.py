from django.shortcuts import render
from rest_framework import generics, status
from .serializers import RoomSerializer, CreateRoomSerializer, UpdateRoomSerializer
from .models import Room
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

# Create your views here.
# Write all of our end points in this file 
# Endpoint is location on the web server we are going to 

# Take in a request and returns a response of all the room objects 
class RoomView(generics.ListAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class GetRoom(APIView):
    serializer_class = RoomSerializer
    lookup_url_kwarg = 'code'

    def get(self, request, format=None):
        # request.GET is getting info about the url from get(self.lookup_url_kwarg)
        # get(self.lookup_url_kwarg) looking for any parameters in the url and look for one that matches 'code'
        code = request.GET.get(self.lookup_url_kwarg)

        # If the room exists, find which room has this code 
        if code != None:
            room = Room.objects.filter(code=code)

            # Serlalize the first entry in the room and extract the data 
            if len(room) > 0:
                data = RoomSerializer(room[0]).data 
                data['is_host'] = self.request.session.session_key == room[0].host
                return Response(data, status=status.HTTP_200_OK)
            return Response({'Room Not Found': 'Invalid Room Code.'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({'Bad Request': 'Code parameter not found in request'}, status=status.HTTP_400_BAD_REQUEST)


class JoinRoom(APIView):
    lookup_url_kwarg = 'code'

    # Post they are joining the room 
    def post(self, request, format=None):
        # Check if user has active session, if not, create one 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        # POST request for the room code 
        code = request.data.get(self.lookup_url_kwarg)
        # Check if we have a room code
        if code != None:
            room_result = Room.objects.filter(code=code) # Find the room we are searching for 
            if len(room_result) > 0:
                room = room_result[0]
                self.request.session['room_code'] = code # Note on backend that the user in this session is in this room 
                # Return message
                return Response({'message': 'Room Joined!'}, status=status.HTTP_200_OK)
            
            return Response({'Bad Request': 'Invalid Room Code'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({'Bad Request': 'Invalid post data, did not find a code key'}, status=status.HTTP_400_BAD_REQUEST)

class CreateRoomView(APIView):
    serializer_class = CreateRoomSerializer

    def post(self, request, format=None):
        # If current user doesnt have active session, create one 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()
        
        # Checks if data sent is valid 
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            host = self.request.session.session_key
            queryset = Room.objects.filter(host=host)
            if queryset.exists():
                room = queryset[0]
                room.guest_can_pause = guest_can_pause
                room.votes_to_skip = votes_to_skip

                # If updating a save object, pass update_fields wit the fields you want to update 
                room.save(update_fields=['guest_can_pause', 'votes_to_skip'])

                # When room is created, also note that theyre host of the room, and store room session 
                self.request.session['room_code'] = room.code 

                return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)
            else:
                room = Room(host=host, guest_can_pause=guest_can_pause, votes_to_skip=votes_to_skip)
                room.save()
                self.request.session['room_code'] = room.code 
                # Send back room created 
                return Response(RoomSerializer(room).data, status=status.HTTP_201_CREATED)

        return Response({'Bad Request': 'Invalid data...'}, status=status.HTTP_400_BAD_REQUEST)

# If user is in room, get room code 
class UserInRoom(APIView):
    def get(self, request, format=None):
        # If current user doesnt have active session, create one 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        data = {
            'code': self.request.session.get('room_code')
        }
        return JsonResponse(data, status=status.HTTP_200_OK)

class LeaveRoom(APIView):
    def post(self, request, format=None):
        # Check if user is host of room
        if 'room_code' in self.request.session:
            self.request.session.pop('room_code') # Remove room code from the session 
            host_id = self.request.session.session_key
            room_results = Room.objects.filter(host=host_id)

            # if host, delete room 
            if len(room_results) > 0:
                room = room_results[0]
                room.delete()

        return Response({'Message': 'Success'}, status=status.HTTP_200_OK)

class UpdateRoom(APIView):
    serializer_class = UpdateRoomSerializer

    def patch(self, request,  format=None):
        # If current user doesnt have active session, create one 
        if not self.request.session.exists(self.request.session.session_key):
            self.request.session.create()

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            guest_can_pause = serializer.data.get('guest_can_pause')
            votes_to_skip = serializer.data.get('votes_to_skip')
            code = serializer.data.get('code')

            # Find any room that has this code 
            queryset = Room.objects.filter(code=code)
            if not queryset.exists():
                return Response({'msg': 'Room not found.'}, status=status.HTTP_400_BAD_REQUEST)

            room = queryset[0]
            user_id = self.request.session.session_key

            # if user is not the host 
            if room.host != user_id:
                return Response({'msg': 'You are not the host of this room.'}, status=status.HTTP_403_FORBIDDEN)

            room.guest_can_pause = guest_can_pause
            room.votes_to_skip = votes_to_skip
            room.save(update_fields=['guest_can_pause', 'votes_to_skip'])
            return Response(RoomSerializer(room).data, status=status.HTTP_200_OK)

        return Response({'Bad Request': "Invalid Data....="}, status=status.HTTP_400_BAD_REQUEST)