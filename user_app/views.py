from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import logout as django_logout
from django.contrib import messages
from django.contrib.auth.models import User
import re
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from .models import Userinfo
from django.contrib.auth import login as auth_login, logout as auth_logout


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = Userinfo.objects.get(email=email)  # Find user by email
            if check_password(password, user.password):  # Check password hash
                request.session.flush()  # Prevent session fixation attacks
                request.session['user_id'] = user.id  # Store user ID in session
                return redirect('user_app:user_dashboard')  # Redirect to profile page
            else:
                messages.error(request, "Invalid email or password.")
        except Userinfo.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    return render(request, 'login.html')


def logout_view(request):
    django_logout(request)
    return redirect('user_app:login') 


def register(request):
    if request.method == "POST":
        try:
            username = request.POST.get("username", "").strip()
            email = request.POST.get("email", "").strip()
            phone = request.POST.get("phone", "").strip()
            # membership_type = request.POST.get("membership_type")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            email_regex = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
            phone_regex = r"^\+?\d{10,15}$"
            strong_password_regex = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
            if len(username) < 3:
                messages.error(request, "Full Name must be at least 3 characters long.")
                return redirect("user_app:register")
            if not re.match(email_regex, email):
                messages.error(request, "Enter a valid email address.")
                return redirect("user_app:register")
            if Userinfo.objects.filter(email=email).exists():
                messages.error(request, "This email is already registered.")
                return redirect("user_app:register")
            if phone and not re.match(phone_regex, phone):
                messages.error(request, "Enter a valid phone number.")
                return redirect("user_app:register")
            # if not membership_type:
            #     messages.error(request, "Please select a Membership Type.")
            #     return redirect("user_app:register")

            if not re.match(strong_password_regex, password):
                messages.error(request, "Password must be at least 8 characters long, include uppercase, lowercase, a number, and a symbol.")
                return redirect("user_app:register")

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return redirect("user_app:register")

            # Create User
            user = Userinfo.objects.create_user(username=email, email=email, password=password)
            user.first_name = username  # Storing full name
            user.save()

            messages.success(request, "Account created successfully! You can now log in.")
            return redirect("user_app:login")

        except IntegrityError:
            messages.error(request, "A user with this email already exists.")
            return redirect("user_app:register")

        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {str(e)}")
            return redirect("user_app:register")

    return render(request, "register.html")


def pricing(request):
    return render(request, "pricing.html")


def try_free(request):
    return render(request, "try_free.html")


def contact(request):
    return render(request, "contact.html")


def features(request):
    return render(request, "features.html")


def terms(request):
    return render(request, "terms.html")


def privacy_policy(request):
    return render(request, "privacy_policy.html")


def user_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_app:login')

    try:
        user = Userinfo.objects.get(id=user_id)
        return render(request, "user_profile.html", {"user": user})
    except Userinfo.DoesNotExist:
        return redirect('user_app:login')


def settings(request):
    user = request.user
    # You can pass the user's payments and membership type here
    return render(request, "settings.html", {'user': user})


def user_dashboard(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('user_app:login')

    try:
        user = Userinfo.objects.get(id=user_id)
        return render(request, "user_dashboard.html", {"user": user})
    except Userinfo.DoesNotExist:
        return redirect('user_app:login')


def edit_profile(request):
    user = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.username = request.POST.get('username', '')
        user.email = request.POST.get('email', '')
        user.phone = request.POST.get('phone', '')
        user.membership_type = request.POST.get('membership_type', '')
        user.save()
        return redirect('user_app:user_profile')
    return render(request, 'edit_profile.html', {'user': user})