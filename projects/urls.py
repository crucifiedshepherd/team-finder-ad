from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_board, name="list"),
    path("create-project/", views.project_studio, name="create"),
    path("skills/", views.skill_suggestions, name="skill_suggestions"),
    path("<int:pk>/", views.project_page, name="detail"),
    path("<int:pk>/edit/", views.project_studio, name="edit"),
    path("<int:pk>/complete/", views.finish_project, name="complete"),
    path(
        "<int:pk>/toggle-participate/",
        views.toggle_my_participation,
        name="toggle_participate",
    ),
    path("<int:pk>/skills/add/", views.attach_project_skill, name="skill_add"),
    path(
        "<int:pk>/skills/<int:skill_id>/remove/",
        views.detach_project_skill,
        name="skill_remove",
    ),
]
