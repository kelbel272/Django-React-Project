from django.db import models
import string
import random

# Everytime we create a room, want a random 8 digit code created 
def generate_unique_code():
    length = 6

    # While true, generate a random code all in uppercase in k length
    while True:
        code = ''.join(random.choices(string.ascii_uppercase, k=length))

        # return list of all things that fit critera , generates code 
        if Room.objects.filter(code=code).count() == 0:
            break

    return code

# Create your models here.
#pieces of info we wanna store for each room 
class Room(models.Model):
    # Store a bunch of characters 
    # check django documentation for all of these 
    code = models.CharField(max_length=8, default=generate_unique_code, unique=True)

    # Only one host for one room 
    host = models.CharField(max_length=50, unique=True)

    # Permission where guest can pause the music 
    guest_can_pause = models.BooleanField(null=False, default=False)

    votes_to_skip = models.IntegerField(null=False, default=1)

    #whenever we add new room , automatcally add date and time it is created 
    created_at = models.DateTimeField(auto_now_add=True)

    #Store currently playing song 
    current_song = models.CharField(max_length=50, null=True)
