from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import EmailLoginForm, ProfileEditForm, SignUpForm
from .models import User

PARTICIPANTS_PER_PAGE = 12


def join_platform(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("projects:list")
    else:
        form = SignUpForm()
    return render(request, "users/register.html", {"form": form})


def enter_account(request):
    if request.method == "POST":
        form = EmailLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:list")
    else:
        form = EmailLoginForm(request)
    return render(request, "users/login.html", {"form": form})


def leave_account(request):
    logout(request)
    return redirect("projects:list")


def member_card(request, pk):
    member = get_object_or_404(User, pk=pk)
    return render(request, "users/user-details.html", {"user": member})


def member_directory(request):
    members = User.objects.order_by("-id")
    paginator = Paginator(members, PARTICIPANTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "users/participants.html",
        {"participants": page_obj, "page_obj": page_obj},
    )


@login_required
def edit_my_profile(request):
    if request.method == "POST":
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, "users/edit_profile.html", {"form": form})


@login_required
def update_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", pk=request.user.pk)
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, "users/change_password.html", {"form": form})
