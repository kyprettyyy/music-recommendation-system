from django.contrib import admin
from django.urls import path
from music import api
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", api.home), path("project", api.home),
    path("admin/", admin.site.urls),
    path("api/tracks", api.catalog),
    path("api/interactions", api.interaction),
    path("api/recommendations", api.recommendations),
    path("accounts/signup/", api.signup),
    path("accounts/login/", auth_views.LoginView.as_view()),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]
