from django.core.management.base import BaseCommand
from django.db import transaction

from projects.models import Project, Skill
from users.models import User

DEMO_PASSWORD = "password123"

DEMO_USERS = [
    {
        "email": "anna.volkova@example.com",
        "name": "Анна",
        "surname": "Волкова",
        "about": "Backend-разработчик, люблю Django и чистую архитектуру.",
        "github_url": "https://github.com/annavolkova",
    },
    {
        "email": "igor.semenov@example.com",
        "name": "Игорь",
        "surname": "Семенов",
        "about": "Frontend-разработчик, специализируюсь на React и TypeScript.",
        "github_url": "https://github.com/igorsemenov",
    },
    {
        "email": "marina.li@example.com",
        "name": "Марина",
        "surname": "Ли",
        "about": "UX/UI-дизайнер, делаю интерфейсы понятными и красивыми.",
        "github_url": "https://github.com/marinali",
    },
    {
        "email": "pavel.gusev@example.com",
        "name": "Павел",
        "surname": "Гусев",
        "about": "DevOps-инженер, обожаю автоматизацию и Docker.",
        "github_url": "https://github.com/pavelgusev",
    },
    {
        "email": "elena.bondareva@example.com",
        "name": "Елена",
        "surname": "Бондарева",
        "about": "Аналитик данных, работаю с Python и SQL.",
        "github_url": "https://github.com/elenabondareva",
    },
]

DEMO_PROJECTS = [
    {
        "owner_email": "anna.volkova@example.com",
        "name": "TeamFinder API",
        "description": "Бэкенд для поиска единомышленников на pet-проекты.",
        "github_url": "https://github.com/annavolkova/teamfinder-api",
        "status": Project.STATUS_OPEN,
        "skills": ["Python", "Django", "PostgreSQL"],
    },
    {
        "owner_email": "igor.semenov@example.com",
        "name": "Conference Planner",
        "description": "Веб-приложение для планирования расписания митапов.",
        "github_url": "https://github.com/igorsemenov/conference-planner",
        "status": Project.STATUS_OPEN,
        "skills": ["React", "TypeScript", "Figma"],
    },
    {
        "owner_email": "marina.li@example.com",
        "name": "Recipe Garden",
        "description": "Каталог рецептов с дизайн-системой для еды и кулинарии.",
        "github_url": "https://github.com/marinali/recipe-garden",
        "status": Project.STATUS_CLOSED,
        "skills": ["Figma", "UX Research"],
    },
    {
        "owner_email": "pavel.gusev@example.com",
        "name": "Deploy Toolkit",
        "description": "Набор скриптов для быстрого деплоя Django-проектов в Docker.",
        "github_url": "https://github.com/pavelgusev/deploy-toolkit",
        "status": Project.STATUS_OPEN,
        "skills": ["Docker", "CI/CD", "Python"],
    },
    {
        "owner_email": "elena.bondareva@example.com",
        "name": "Habit Tracker Analytics",
        "description": "Дашборд для анализа привычек пользователей трекера.",
        "github_url": "https://github.com/elenabondareva/habit-analytics",
        "status": Project.STATUS_OPEN,
        "skills": ["Python", "SQL", "Pandas"],
    },
]


class Command(BaseCommand):
    help = "Создаёт демонстрационных пользователей и проекты для TeamFinder."

    @transaction.atomic
    def handle(self, *args, **options):
        users_by_email = {}
        for data in DEMO_USERS:
            user, created = User.objects.get_or_create(
                email=data["email"],
                defaults={
                    "name": data["name"],
                    "surname": data["surname"],
                    "about": data["about"],
                    "github_url": data["github_url"],
                },
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                user.save()
                self.stdout.write(f"Создан пользователь {user.email}")
            users_by_email[user.email] = user

        for data in DEMO_PROJECTS:
            owner = users_by_email[data["owner_email"]]
            project, created = Project.objects.get_or_create(
                name=data["name"],
                owner=owner,
                defaults={
                    "description": data["description"],
                    "github_url": data["github_url"],
                    "status": data["status"],
                },
            )
            if created:
                project.participants.add(owner)
                for skill_name in data["skills"]:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    project.skills.add(skill)
                self.stdout.write(f"Создан проект «{project.name}»")

        self.stdout.write(self.style.SUCCESS("Демо-данные готовы."))
