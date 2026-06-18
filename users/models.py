import io
import random

from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)

from PIL import Image, ImageDraw, ImageFont


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, name, surname, phone, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(
            email=email, name=name, surname=surname, phone=phone or None, **extra_fields
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
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, name, surname, phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to="avatars/", blank=True)
    phone = models.CharField(max_length=12, unique=True, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(blank=True, max_length=256)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    def __str__(self):
        return f"{self.surname} {self.name} <{self.email}>"

    def save(self, *args, **kwargs):
        if not self.avatar:
            try:
                self._generate_avatar()
            except Exception:
                # avatar generation should not block saving
                pass
        super().save(*args, **kwargs)

    def _generate_avatar(self):
        """Generate a simple avatar with first letter on colored background."""
        letter = (self.name or "?")[0].upper()
        size = (200, 200)
        palette = [
            (52, 152, 219),
            (46, 204, 113),
            (155, 89, 182),
            (241, 196, 15),
            (26, 188, 156),
            (230, 126, 34),
        ]
        bg = random.choice(palette)
        img = Image.new("RGB", size, bg)
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 100)
        except Exception:
            font = ImageFont.load_default()
        left, top, right, bottom = draw.textbbox((0, 0), letter, font=font)
        w, h = right - left, bottom - top
        position = ((size[0] - w) / 2 - left, (size[1] - h) / 2 - top)
        draw.text(position, letter, fill=(255, 255, 255), font=font)
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        name = f"av_{self.email.replace('@', '_')}.png"
        self.avatar.save(name, ContentFile(buffer.read()), save=False)
        buffer.close()
