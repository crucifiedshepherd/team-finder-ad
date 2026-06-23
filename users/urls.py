from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path("register/", views.join_platform, name="register"),
    path("login/", views.enter_account, name="login"),
    path("logout/", views.leave_account, name="logout"),
    path("list/", views.member_directory, name="list"),
    path("edit-profile/", views.edit_my_profile, name="edit_profile"),
    path("change-password/", views.update_password, name="change_password"),
    path("<int:user_pk>/", views.member_card, name="detail"),
]
