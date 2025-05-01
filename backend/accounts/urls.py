from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("api/check-auth/", views.check_auth, name="check_auth"),
    path("api/activities/", views.get_activities, name="get_activities"),
]