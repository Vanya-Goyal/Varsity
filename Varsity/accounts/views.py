from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from courses.models import Course
from .models import CustomUser


def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            role = form.cleaned_data.get('role')

            if role == 'instructor':
                user.is_staff = True
            user.save()

            
            return redirect('accounts:login')  

    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'student':
                return redirect('accounts:student_dashboard') 
            elif user.role == 'instructor':
                return redirect('instructors:dashboard')  
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@login_required
def student_dashboard(request):
    enrolled_courses = Course.objects.filter(students=request.user)
    return render(request, 'accounts/student_dashboard.html', {
        'enrolled_courses': enrolled_courses
    })
@login_required
def instructor_dashboard(request):
    if request.user.role != 'instructor':
        return HttpResponseForbidden("You are not authorized to view this page.")
    return render(request, 'instructors/dashboard.html')

