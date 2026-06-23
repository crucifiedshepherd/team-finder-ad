from django.urls import path

from . import views

app_name = "projects"

urlpatterns = [
    path("list/", views.project_board, name="list"),
    path("create-project/", views.create_project, name="create"),
    path("skills/", views.skill_suggestions, name="skill_suggestions"),
    path("<int:project_pk>/", views.project_page, name="detail"),
    path("<int:project_pk>/edit/", views.edit_project, name="edit"),
    path("<int:project_pk>/complete/", views.finish_project, name="complete"),
    path(
        "<int:project_pk>/toggle-participate/",
        views.toggle_my_participation,
        name="toggle_participate",
    ),
    path("<int:project_pk>/skills/add/", views.attach_project_skill, name="skill_add"),
    path(
        "<int:project_pk>/skills/<int:skill_pk>/remove/",
        views.detach_project_skill,
        name="skill_remove",
    ),
]
