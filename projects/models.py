from django.conf import settings
from django.db import models


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_projects"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = [(STATUS_OPEN, "Открыт"), (STATUS_CLOSED, "Закрыт")]
    status = models.CharField(max_length=6, choices=STATUS_CHOICES, default=STATUS_OPEN)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="participated_projects", blank=True
    )

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)
    projects = models.ManyToManyField(Project, related_name="skills", blank=True)

    def __str__(self):
        return self.name
