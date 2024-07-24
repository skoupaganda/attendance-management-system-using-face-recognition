from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from .forms import RegisterUserForm , CustomPasswordChangeForm
import base64
import face_recognition
import numpy as np
from django.contrib.auth import update_session_auth_hash


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"You have successfully logged in, {request.user.first_name} {request.user.last_name}!")
            return redirect('home')
        else:
            messages.error(request, "Failed to log in, please try again!")
            return redirect('login')
    return render(request, 'authenticate/login.html')

def register_user(request):
    if request.method == "POST":
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username is already taken.")
                return render(request, 'authenticate/register_user.html', {'form': form})

            profile_picture_data = form.cleaned_data.get('profile_picture')
            if profile_picture_data:
                format, imgstr = profile_picture_data.split(';base64,')
                ext = format.split('/')[-1]
                file = ContentFile(base64.b64decode(imgstr), name='profile_picture.' + ext)

                # Load the image and detect face
                image = face_recognition.load_image_file(file)
                face_encodings = face_recognition.face_encodings(image)
                if not face_encodings:
                    messages.error(request, "No face found in the photo. Please upload a photo with a clear face.")
                    return render(request, 'authenticate/register_user.html', {'form': form})
                if len(face_encodings) > 1:
                    messages.error(request, "Multiple faces found in the photo. Please upload a photo with only one face.")
                    return render(request, 'authenticate/register_user.html', {'form': form})

            user = form.save()
            if profile_picture_data:
                user.profile.profile_picture.save(file.name, file)
                user.profile.encoding = face_encodings[0].tobytes()
                user.profile.save()

            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "Registration successful!")
                return redirect('home')
            else:
                messages.error(request, "Authentication failed, please try again.")
        else:
            messages.error(request, "Registration failed. Please correct the error below.")
    else:
        form = RegisterUserForm()
    return render(request, 'authenticate/register_user.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, "You have successfully logged out!")
    return redirect('index')

@login_required
def update_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  
            messages.success(request, 'Your password was successfully updated!')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'authenticate/update_password.html', {'form': form})