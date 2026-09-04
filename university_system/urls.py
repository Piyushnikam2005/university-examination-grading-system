"""
URL configuration for university_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from django.shortcuts import redirect

from academics import views


def home(request):
    if request.user.is_authenticated:
        return redirect("create_exam")
    return redirect("login")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),

    path("exam/create/", views.create_exam, name="create_exam"),
    path("exam/success/", views.exam_success, name="exam_success"),
    path("grades/enter/<int:exam_id>/", views.enter_grades, name="enter_grades"),
    path("grades/download/<int:exam_id>/", views.download_grade_csv, name="download_grade_csv"),
    path("grades/upload/<int:exam_id>/", views.upload_grade_csv, name="upload_grade_csv"),
    path("grades/summary/<int:exam_id>/", views.grade_summary, name="grade_summary"),
    path("grades/student/<int:student_id>/", views.student_report, name="student_report"),
]
