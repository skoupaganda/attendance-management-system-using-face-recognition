from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ProfileUpdateForm
from .models import Attendance , Profile
from django.contrib.auth.models import User
import face_recognition
import cv2
from django.http import JsonResponse
import numpy as np
import base64
from django.core.files.base import ContentFile
from django.db.models import Count
from django.utils import timezone




def index(request):
    return render(request, 'attendance/index.html')

def about(request):
    return render(request, 'attendance/about.html')

def services(request):
    return render(request, 'attendance/services.html')





@login_required
def home(request):
    return render(request, 'attendance/home.html')

@login_required
def profile(request):
    if request.method == "POST":
        form = ProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            if User.objects.filter(username=username).exclude(pk=request.user.pk).exists():
                messages.error(request, "Username is already taken.")
                return render(request, 'attendance/profile.html', {'form': form})

            profile_picture_data = request.POST.get('profile_picture')
            if profile_picture_data:
                format, imgstr = profile_picture_data.split(';base64,')
                ext = format.split('/')[-1]
                file = ContentFile(base64.b64decode(imgstr), name='profile_picture.' + ext)

                # Load the image and detect face
                image = face_recognition.load_image_file(file)
                face_encodings = face_recognition.face_encodings(image)
                if not face_encodings:
                    messages.error(request, "No face found in the photo. Please upload a photo with a clear face.")
                    return render(request, 'attendance/profile.html', {'form': form})
                if len(face_encodings) > 1:
                    messages.error(request, "Multiple faces found in the photo. Please upload a photo with only one face.")
                    return render(request, 'attendance/profile.html', {'form': form})

            user = form.save()
            if profile_picture_data:
                if hasattr(user, 'profile'):
                    user.profile.profile_picture.save(file.name, file)
                    user.profile.encoding = face_encodings[0].tobytes()
                    user.profile.save()
                else:
                    profile = Profile(user=user, profile_picture=file, encoding=face_encodings[0].tobytes())
                    profile.save()
            messages.success(request, "Profile updated successfully")
            return redirect('home')
        else:
            messages.error(request, "Profile update failed. Please correct the error below.")
    else:
        form = ProfileUpdateForm(instance=request.user)
    return render(request, 'attendance/profile.html', {'form': form})

@login_required
def delete_profile(request):
    user = request.user
    user.delete()
    messages.success(request, "Profile deleted successfully")
    return redirect('index')

@login_required
def dashboard(request):
    attendance_data = Attendance.objects.filter(user=request.user).select_related('user').order_by('-timestamp')
    return render(request, 'attendance/dashboard.html', {'attendance_data': attendance_data})



@login_required
def take_attendance(request):
    if request.method == 'POST':
        user = request.user
        data_url = request.POST.get('image')

        if data_url:
            try:
                # Decode the base64 image data
                format, imgstr = data_url.split(';base64,')
                img_data = base64.b64decode(imgstr)
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                # Convert image to RGB (OpenCV uses BGR by default)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # Find face locations and encodings
                face_locations = face_recognition.face_locations(img)
                
                if len(face_locations) != 1:
                    messages.warning(request, 'No face detected or multiple faces detected. Please try again.')
                    return redirect('take_attendance')
                
                img_encoding = face_recognition.face_encodings(img, face_locations)[0]
                
                # Compare with profile picture encoding
                profile = Profile.objects.get(user=user)
                profile_image = face_recognition.load_image_file(profile.profile_picture.path)
                profile_encodings = face_recognition.face_encodings(profile_image)

                if not profile_encodings:
                    messages.warning(request, 'No face encoding found in the profile picture. Please update your profile picture.')
                    return redirect('profile')

                profile_encoding = profile_encodings[0]
                
                # Use face distance to determine match
                face_distance = face_recognition.face_distance([profile_encoding], img_encoding)[0]
                match = face_distance < 0.4  # Adjust threshold as needed for stricter matching
                
                if match:
                    # Check if the user has already marked attendance today
                    today = timezone.now().date()
                    if Attendance.objects.filter(user=user, timestamp__date=today).exists():
                        messages.warning(request, f'You have already marked your attendance for today, {user.first_name} {user.last_name}!')
                        return redirect('dashboard')
                    
                    # Mark attendance
                    Attendance.objects.create(user=user)
                    messages.success(request, 'Attendance marked successfully!')
                    return redirect('dashboard')
                else:
                    messages.warning(request, 'Face does not match the profile picture. Please try again!')
                    return redirect('take_attendance')
            except Profile.DoesNotExist:
                messages.warning(request, 'Profile not found. Please update your profile.')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'An error occurred: {e}')
                return redirect('take_attendance')
        else:
            messages.error(request, 'Failed to capture the image. Please try again.')
            return redirect('take_attendance')
    
    return render(request, 'attendance/take_attendance.html')