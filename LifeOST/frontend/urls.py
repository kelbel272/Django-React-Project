from django.urls import path
from .views import index

app_name = 'frontend'

# Dispatches urls to correct application 
urlpatterns = [
    path('', index, name=''),  # Render index template whenever we have a blank path (essentially homepage)
    path('info', index),
    path('join', index),
    path('create', index),
    path('room/<str:roomCode>', index) #dynamic url 
]
