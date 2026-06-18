import re
from urllib.parse import urlparse

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import User

PHONE_PATTERN = re.compile(r"^(?:8|\+7)(\d{10})$")
GITHUB_HOSTS = {"github.com", "www.github.com"}


def normalize_phone(value):
    match = PHONE_PATTERN.match(value)
    if not match:
        raise ValidationError("Введите номер телефона в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
    return "+7" + match.group(1)


def validate_github_url(value):
    validator = URLValidator(schemes=["http", "https"])
    validator(value)
    host = urlparse(value).hostname or ""
    if host.lower() not in GITHUB_HOSTS:
        raise ValidationError("Ссылка должна вести на github.com.")


class SignUpForm(forms.ModelForm):
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")

    def clean_password(self):
        password = self.cleaned_data["password"]
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class EmailLoginForm(forms.Form):
    email = forms.EmailField(label="Email")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)
            if self.user_cache is None:
                raise ValidationError("Неверный имейл или пароль.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {"about": forms.Textarea(attrs={"rows": 4})}
        error_messages = {
            "phone": {
                "unique": "Этот номер телефона уже используется другим пользователем.",
            },
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        return normalize_phone(phone)

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url")
        if not github_url:
            return github_url
        validate_github_url(github_url)
        return github_url


class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Password confirmation", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "name", "surname", "phone")

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords don't match")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ("email", "password", "name", "surname", "phone", "is_active", "is_staff")
