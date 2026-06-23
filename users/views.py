from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.shortcuts import get_object_or_404, redirect, render

from team_finder.constants import PARTICIPANTS_PER_PAGE
from team_finder.utils import get_page_obj

from .forms import EmailLoginForm, ProfileEditForm, SignUpForm
from .models import User


def join_platform(request):
    form = SignUpForm(request.POST or None)
    if not form.is_valid():
        return render(request, "users/register.html", {"form": form})

    user = form.save()
    login(request, user)
    return redirect("projects:list")


def enter_account(request):
    form = EmailLoginForm(request, data=request.POST or None)
    if not form.is_valid():
        return render(request, "users/login.html", {"form": form})

    login(request, form.get_user())
    return redirect("projects:list")


def leave_account(request):
    logout(request)
    return redirect("projects:list")


def member_card(request, user_pk):
    member = get_object_or_404(User, pk=user_pk)
    return render(request, "users/user-details.html", {"user": member})


def member_directory(request):
    members = User.objects.all()
    page_obj = get_page_obj(request, members, PARTICIPANTS_PER_PAGE)
    return render(
        request,
        "users/participants.html",
        {"participants": page_obj, "page_obj": page_obj},
    )


@login_required
def edit_my_profile(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user,
    )
    if not form.is_valid():
        return render(request, "users/edit_profile.html", {"form": form})

    form.save()
    return redirect("users:detail", user_pk=request.user.pk)


@login_required
def update_password(request):
    form = PasswordChangeForm(user=request.user, data=request.POST or None)
    if not form.is_valid():
        return render(request, "users/change_password.html", {"form": form})

    user = form.save()
    update_session_auth_hash(request, user)
    return redirect("users:detail", user_pk=request.user.pk)
