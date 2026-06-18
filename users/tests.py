from django.urls import reverse

import pytest

from .models import User


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_generates_avatar(self):
        user = User.objects.create_user(
            email="walker@example.com",
            name="Иван",
            surname="Петров",
            password="strong-pass-123",
        )

        assert user.pk is not None
        assert user.phone is None
        assert user.avatar
        assert user.check_password("strong-pass-123")

    def test_create_superuser_flags(self):
        admin = User.objects.create_superuser(
            email="root@example.com",
            name="Root",
            surname="Admin",
            password="root-pass-123",
        )

        assert admin.is_staff is True
        assert admin.is_superuser is True


@pytest.mark.django_db
class TestRegistration:
    def test_register_creates_user_and_logs_in(self, client):
        response = client.post(
            reverse("users:register"),
            {
                "name": "Светлана",
                "surname": "Орлова",
                "email": "svetlana@example.com",
                "password": "registration-pass-1",
            },
        )

        assert response.status_code == 302
        assert User.objects.filter(email="svetlana@example.com").exists()
        assert response.wsgi_request.user.is_authenticated

    def test_register_rejects_duplicate_email(self, client):
        User.objects.create_user(
            email="taken@example.com", name="Имя", surname="Фамилия", password="first-pass-1"
        )

        response = client.post(
            reverse("users:register"),
            {
                "name": "Другой",
                "surname": "Пользователь",
                "email": "taken@example.com",
                "password": "second-pass-1",
            },
        )

        assert response.status_code == 200
        assert User.objects.filter(email="taken@example.com").count() == 1


@pytest.mark.django_db
class TestLoginLogout:
    def setup_method(self):
        self.password = "login-pass-123"

    def test_login_with_correct_credentials(self, client):
        User.objects.create_user(
            email="login@example.com", name="Олег", surname="Жуков", password=self.password
        )

        response = client.post(
            reverse("users:login"), {"email": "login@example.com", "password": self.password}
        )

        assert response.status_code == 302
        assert response.wsgi_request.user.is_authenticated

    def test_login_with_wrong_password_shows_error(self, client):
        User.objects.create_user(
            email="login2@example.com", name="Олег", surname="Жуков", password=self.password
        )

        response = client.post(
            reverse("users:login"), {"email": "login2@example.com", "password": "wrong-pass"}
        )

        assert response.status_code == 200
        assert not response.wsgi_request.user.is_authenticated

    def test_logout_redirects_to_project_list(self, client):
        user = User.objects.create_user(
            email="logout@example.com", name="Олег", surname="Жуков", password=self.password
        )
        client.force_login(user)

        response = client.get(reverse("users:logout"))

        assert response.status_code == 302
        assert reverse("projects:list") in response.url


@pytest.mark.django_db
class TestProfileEditing:
    def setup_method(self):
        self.password = "profile-pass-123"

    def test_phone_is_normalized_to_plus_seven_format(self, client):
        user = User.objects.create_user(
            email="profile@example.com", name="Анна", surname="Соколова", password=self.password
        )
        client.force_login(user)

        response = client.post(
            reverse("users:edit_profile"),
            {
                "name": user.name,
                "surname": user.surname,
                "about": "",
                "phone": "89991234567",
                "github_url": "",
            },
        )

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.phone == "+79991234567"

    def test_duplicate_phone_is_rejected(self, client):
        User.objects.create_user(
            email="owner@example.com",
            name="Первый",
            surname="Пользователь",
            password=self.password,
            phone="+79991234567",
        )
        user = User.objects.create_user(
            email="second@example.com",
            name="Второй",
            surname="Пользователь",
            password=self.password,
        )
        client.force_login(user)

        response = client.post(
            reverse("users:edit_profile"),
            {
                "name": user.name,
                "surname": user.surname,
                "about": "",
                "phone": "89991234567",
                "github_url": "",
            },
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.phone is None

    def test_github_url_must_point_to_github(self, client):
        user = User.objects.create_user(
            email="github@example.com", name="Дима", surname="Котов", password=self.password
        )
        client.force_login(user)

        response = client.post(
            reverse("users:edit_profile"),
            {
                "name": user.name,
                "surname": user.surname,
                "about": "",
                "phone": "",
                "github_url": "https://gitlab.com/dima",
            },
        )

        assert response.status_code == 200
        user.refresh_from_db()
        assert user.github_url == ""

    def test_valid_github_url_is_saved(self, client):
        user = User.objects.create_user(
            email="github2@example.com", name="Дима", surname="Котов", password=self.password
        )
        client.force_login(user)

        response = client.post(
            reverse("users:edit_profile"),
            {
                "name": user.name,
                "surname": user.surname,
                "about": "",
                "phone": "",
                "github_url": "https://github.com/dima",
            },
        )

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.github_url == "https://github.com/dima"


@pytest.mark.django_db
class TestPasswordChange:
    def test_user_can_change_password(self, client):
        user = User.objects.create_user(
            email="password@example.com",
            name="Юлия",
            surname="Морозова",
            password="old-pass-123",
        )
        client.force_login(user)

        response = client.post(
            reverse("users:change_password"),
            {
                "old_password": "old-pass-123",
                "new_password1": "new-pass-456",
                "new_password2": "new-pass-456",
            },
        )

        assert response.status_code == 302
        user.refresh_from_db()
        assert user.check_password("new-pass-456")


@pytest.mark.django_db
class TestMemberDirectory:
    def test_member_list_and_detail_pages_render(self, client):
        user = User.objects.create_user(
            email="member@example.com", name="Лена", surname="Громова", password="member-pass-1"
        )

        list_response = client.get(reverse("users:list"))
        detail_response = client.get(reverse("users:detail", kwargs={"pk": user.pk}))

        assert list_response.status_code == 200
        assert detail_response.status_code == 200
        assert "Громова" in detail_response.content.decode()

    def test_pagination_splits_participants_across_pages(self, client):
        for index in range(15):
            User.objects.create_user(
                email=f"participant{index}@example.com",
                name=f"Имя{index}",
                surname=f"Фамилия{index}",
                password="participant-pass-1",
            )

        first_page = client.get(reverse("users:list"))
        second_page = client.get(reverse("users:list"), {"page": 2})

        assert len(first_page.context["page_obj"].object_list) == 12
        assert len(second_page.context["page_obj"].object_list) == 3

    def test_participants_sorted_newest_first(self, client):
        older = User.objects.create_user(
            email="older@example.com", name="Старый", surname="Участник", password="pass-12345"
        )
        newer = User.objects.create_user(
            email="newer@example.com", name="Новый", surname="Участник", password="pass-12345"
        )

        response = client.get(reverse("users:list"))

        participants = list(response.context["page_obj"].object_list)
        assert participants.index(newer) < participants.index(older)
