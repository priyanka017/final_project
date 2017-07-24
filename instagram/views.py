from django.shortcuts import render, redirect
from forms import SignUpForm
from models import UserModel
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password

# Create your views here.

def signup_view(request):
    if request.method == "POST":
        return render(request, 'success.html')
    elif request.method == 'GET':
        form = SignUpForm()
        return render(request, 'signup.html', {'form' : form})