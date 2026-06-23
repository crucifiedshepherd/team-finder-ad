import io
import random

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from team_finder.constants import (
    AVATAR_FONT_SIZE,
    AVATAR_PALETTE,
    AVATAR_SIZE,
    AVATAR_TEXT_COLOR,
    PHONE_MAX_LENGTH,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_SURNAME_MAX_LENGTH,
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, name, surname, phone, password, **extra_fields):
        if not email:
            raise ValueError("Email обязателен.")
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone or None,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, surname, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, name, surname, phone, password, **extra_fields)

    def create_superuser(self, email, name, surname, phone=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("У суперпользователя is_staff должен быть True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("У суперпользователя is_superuser должен быть True.")
        return self._create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("Электронная почта", unique=True)
    name = models.CharField("Имя", max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField("Фамилия", max_length=USER_SURNAME_MAX_LENGTH)
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True)
    phone = models.CharField(
        "Телефон",
        max_length=PHONE_MAX_LENGTH,
        unique=True,
        blank=True,
        null=True,
    )
    github_url = models.URLField("Ссылка на GitHub", blank=True)
    about = models.TextField("О себе", blank=True, max_length=USER_ABOUT_MAX_LENGTH)
    created_at = models.DateTimeField("Дата регистрации", auto_now_add=True)
    is_active = models.BooleanField("Активен", default=True)
    is_staff = models.BooleanField("Персонал", default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.surname} {self.name} <{self.email}>"

    def save(self, *args, **kwargs):
        if not self.avatar:
            try:
                self._generate_avatar()
            except Exception:
                pass
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        letter = (self.name or "?")[0].upper()
        bg = random.choice(AVATAR_PALETTE)
        img = Image.new("RGB", AVATAR_SIZE, bg)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", AVATAR_FONT_SIZE)
        except Exception:
            font = ImageFont.load_default()
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
        width, height = right - left, bottom - top
        position = (
            (AVATAR_SIZE[0] - width) / 2 - left,
            (AVATAR_SIZE[1] - height) / 2 - top,
        )
        draw.text(position, letter, fill=AVATAR_TEXT_COLOR, font=font)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        name = f"av_{self.email.replace('@', '_')}.png"
        self.avatar.save(name, ContentFile(buffer.read()), save=False)
        buffer.close()
