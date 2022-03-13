from django.shortcuts import render

# Create your views here.

# Allows us to render index.html template 
# React will take care of it and start rendering things inside the template 
# Takes the request, takes the template, and return the html to wherever sent the request
def index(request, *args, **kwargs):
    return render(request, 'frontend/index.html')