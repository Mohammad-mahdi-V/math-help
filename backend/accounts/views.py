from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import Activity
from urllib.parse import urlencode
from django.db.utils import IntegrityError
import re

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            sessionid = request.session.session_key
            redirect_url = f"http://localhost:8502/?sessionid={sessionid}"
            return redirect(redirect_url)
        else:
            return render(request, "accounts/login.html", {"error": "نام کاربری یا رمز عبور اشتباه است"})
    return render(request, "accounts/login.html")

def password_strength(password):
    score = 0
    if len(password) >= 8:
        score += 1
    if re.search(r'[a-z]', password):
        score += 1
    if re.search(r'[A-Z]', password):
        score += 1
    if re.search(r'\d', password):
        score += 1
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 1
    return score

def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            return render(request, "accounts/register.html", {"error": "این نام کاربری قبلاً ثبت شده است"})

        strength = password_strength(password)
        if strength < 3:
            return render(request, "accounts/register.html", {
                "error": f"رمز عبور شما ضعیف است (نمره: {strength}/5). رمز باید ترکیبی از حروف کوچک، بزرگ، عدد و نماد باشد."
            })

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            login(request, user)
            sessionid = request.session.session_key
            redirect_url = f"http://localhost:8502/?sessionid={sessionid}"
            return redirect(redirect_url)
        except IntegrityError:
            return render(request, "accounts/register.html", {"error": "خطا در ثبت‌نام، لطفاً نام کاربری دیگری انتخاب کنید"})

    return render(request, "accounts/register.html")

def logout_view(request):
    logout(request)
    return redirect("http://localhost:8502")

def login_redirect_view(request):
    sessionid = request.session.session_key
    return render(request, "accounts/redirect.html", {"sessionid": sessionid})

@api_view(['GET'])
def check_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({
            "is_authenticated": True,
            "username": request.user.username
        })
    return JsonResponse({"is_authenticated": False})

@api_view(['GET'])
def get_activities(request):
    if request.user.is_authenticated:
        activities = Activity.objects.filter(user=request.user).values('activity_data', 'section_name', 'created_at')
        return JsonResponse({"activities": list(activities)})
    return JsonResponse({"error": "User not authenticated"}, status=401)