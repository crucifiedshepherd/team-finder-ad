import json
from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

import pytest

from .models import Project, Skill
from users.models import User


@pytest.fixture
def user(db):
    return User.objects.create_user(
        email="owner@example.com", name="Влад", surname="Тарасов", password="owner-pass-123"
    )


@pytest.fixture
def other_user(db):
    return User.objects.create_user(
        email="other@example.com", name="Настя", surname="Сорокина", password="other-pass-123"
    )


@pytest.fixture
def project(user):
    project = Project.objects.create(name="Альфа", owner=user)
    project.participants.add(user)
    return project


@pytest.mark.django_db
class TestProjectBoard:
    def test_pagination_splits_projects_across_pages(self, client, user):
        for index in range(15):
            Project.objects.create(name=f"Проект {index}", owner=user)

        first_page = client.get(reverse("projects:list"))
        second_page = client.get(reverse("projects:list"), {"page": 2})

        assert len(first_page.context["page_obj"].object_list) == 12
        assert len(second_page.context["page_obj"].object_list) == 3

    def test_skill_filter_returns_only_matching_projects(self, client, user):
        matching = Project.objects.create(name="С навыком", owner=user)
        Project.objects.create(name="Без навыка", owner=user)
        skill = Skill.objects.create(name="Django")
        matching.skills.add(skill)

        response = client.get(reverse("projects:list"), {"skill": "Django"})

        projects = list(response.context["page_obj"].object_list)
        assert projects == [matching]
        assert response.context["active_skill"] == "Django"

    def test_projects_sorted_newest_first(self, client, user):
        older = Project.objects.create(name="Старый", owner=user)
        newer = Project.objects.create(name="Новый", owner=user)
        Project.objects.filter(pk=older.pk).update(
            created_at=timezone.now() - timedelta(days=1)
        )

        response = client.get(reverse("projects:list"))

        projects = list(response.context["page_obj"].object_list)
        assert projects.index(newer) < projects.index(older)


@pytest.mark.django_db
class TestProjectDetail:
    def test_project_detail_renders(self, client, project):
        response = client.get(reverse("projects:detail", kwargs={"pk": project.pk}))

        assert response.status_code == 200
        assert project.name in response.content.decode()


@pytest.mark.django_db
class TestProjectStudio:
    def test_anonymous_user_cannot_create_project(self, client):
        response = client.get(reverse("projects:create"))

        assert response.status_code == 302
        assert reverse("users:login") in response.url

    def test_owner_can_create_project(self, client, user):
        client.force_login(user)

        response = client.post(
            reverse("projects:create"),
            {
                "name": "Новый проект",
                "description": "Описание",
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
        )

        project = Project.objects.get(name="Новый проект")
        assert response.status_code == 302
        assert project.owner == user
        assert project.participants.filter(pk=user.pk).exists()

    def test_owner_can_edit_own_project(self, client, project, user):
        client.force_login(user)

        response = client.post(
            reverse("projects:edit", kwargs={"pk": project.pk}),
            {
                "name": "Обновлённое имя",
                "description": project.description,
                "github_url": "",
                "status": project.status,
            },
        )

        project.refresh_from_db()
        assert response.status_code == 302
        assert project.name == "Обновлённое имя"

    def test_other_user_cannot_edit_project(self, client, project, other_user):
        client.force_login(other_user)

        response = client.get(reverse("projects:edit", kwargs={"pk": project.pk}))

        assert response.status_code == 404

    def test_creating_project_without_name_shows_form_error(self, client, user):
        client.force_login(user)

        response = client.post(
            reverse("projects:create"),
            {
                "name": "",
                "description": "Описание",
                "github_url": "",
                "status": Project.STATUS_OPEN,
            },
        )

        assert response.status_code == 200
        assert "name" in response.context["form"].errors
        assert not Project.objects.filter(description="Описание").exists()


@pytest.mark.django_db
class TestParticipation:
    def test_toggle_participation_adds_and_removes_user(self, client, project, other_user):
        client.force_login(other_user)
        url = reverse("projects:toggle_participate", kwargs={"pk": project.pk})

        first_response = client.post(url)
        assert first_response.status_code == 200
        assert json.loads(first_response.content)["participant"] is True
        assert project.participants.filter(pk=other_user.pk).exists()

        second_response = client.post(url)
        assert json.loads(second_response.content)["participant"] is False
        assert not project.participants.filter(pk=other_user.pk).exists()


@pytest.mark.django_db
class TestFinishProject:
    def test_owner_can_complete_open_project(self, client, project, user):
        client.force_login(user)

        response = client.post(reverse("projects:complete", kwargs={"pk": project.pk}))

        project.refresh_from_db()
        assert response.status_code == 200
        assert project.status == Project.STATUS_CLOSED

    def test_non_owner_cannot_complete_project(self, client, project, other_user):
        client.force_login(other_user)

        response = client.post(reverse("projects:complete", kwargs={"pk": project.pk}))

        project.refresh_from_db()
        assert response.status_code == 400
        assert project.status == Project.STATUS_OPEN

    def test_already_closed_project_cannot_be_completed_again(self, client, project, user):
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        client.force_login(user)

        response = client.post(reverse("projects:complete", kwargs={"pk": project.pk}))

        assert response.status_code == 400


@pytest.mark.django_db
class TestSkillSuggestions:
    def test_suggestions_filter_by_query_prefix(self, client):
        Skill.objects.create(name="Python")
        Skill.objects.create(name="PostgreSQL")
        Skill.objects.create(name="React")

        response = client.get(reverse("projects:skill_suggestions"), {"q": "Po"})

        names = {item["name"] for item in json.loads(response.content)}
        assert names == {"PostgreSQL"}


@pytest.mark.django_db
class TestProjectSkills:
    def test_owner_can_add_existing_skill_by_id(self, client, project, user):
        skill = Skill.objects.create(name="Docker")
        client.force_login(user)

        response = client.post(
            reverse("projects:skill_add", kwargs={"pk": project.pk}),
            data=json.dumps({"skill_id": skill.id}),
            content_type="application/json",
        )

        payload = json.loads(response.content)
        assert response.status_code == 200
        assert payload["added"] is True
        assert payload["created"] is False
        assert project.skills.filter(pk=skill.pk).exists()

    def test_owner_can_add_new_skill_by_name(self, client, project, user):
        client.force_login(user)

        response = client.post(
            reverse("projects:skill_add", kwargs={"pk": project.pk}),
            data=json.dumps({"name": "Kubernetes"}),
            content_type="application/json",
        )

        payload = json.loads(response.content)
        assert payload["created"] is True
        assert payload["added"] is True
        assert project.skills.filter(name="Kubernetes").exists()

    def test_adding_same_skill_twice_is_idempotent(self, client, project, user):
        skill = Skill.objects.create(name="Docker")
        project.skills.add(skill)
        client.force_login(user)

        response = client.post(
            reverse("projects:skill_add", kwargs={"pk": project.pk}),
            data=json.dumps({"skill_id": skill.id}),
            content_type="application/json",
        )

        payload = json.loads(response.content)
        assert payload["added"] is False
        assert project.skills.filter(pk=skill.pk).count() == 1

    def test_non_owner_cannot_add_skill(self, client, project, other_user):
        skill = Skill.objects.create(name="Docker")
        client.force_login(other_user)

        response = client.post(
            reverse("projects:skill_add", kwargs={"pk": project.pk}),
            data=json.dumps({"skill_id": skill.id}),
            content_type="application/json",
        )

        assert response.status_code == 404

    def test_owner_can_remove_skill(self, client, project, user):
        skill = Skill.objects.create(name="Docker")
        project.skills.add(skill)
        client.force_login(user)

        response = client.post(
            reverse("projects:skill_remove", kwargs={"pk": project.pk, "skill_id": skill.id})
        )

        assert response.status_code == 200
        assert not project.skills.filter(pk=skill.pk).exists()
