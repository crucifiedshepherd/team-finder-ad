import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from team_finder.forms import GithubUrlCleanMixin

from .models import User

PHONE_PATTERN = re.compile(r"^(?:8|\+7)(\d{10})$")

def normalize_phone(value):
    match = PHONE_PATTERN.match(value)
    if not match:
        raise ValidationError("Введите номер телефона в формате 8XXXXXXXXXX или +7XXXXXXXXXX.")
    return "+7" + match.group(1)


class PhoneCleanMixin:
    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not phone:
            return None
        return normalize_phone(phone)


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
    email = forms.EmailField(label="Электронная почта")
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
                raise ValidationError("Неверный email или пароль.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileEditForm(PhoneCleanMixin, GithubUrlCleanMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")


class UserCreationForm(PhoneCleanMixin, GithubUrlCleanMixin, forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "name", "surname", "phone", "github_url")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(PhoneCleanMixin, GithubUrlCleanMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "name",
            "surname",
            "phone",
            "github_url",
            "is_active",
            "is_staff",
        )
