import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from team_finder.constants import HTTP_BAD_REQUEST, PROJECTS_PER_PAGE, SUGGESTIONS_LIMIT
from team_finder.utils import get_page_obj

from .forms import ProjectForm
from .models import Project, Skill


def project_board(request):
    projects = Project.objects.select_related("owner")
    active_skill = request.GET.get("skill")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    page_obj = get_page_obj(request, projects, PROJECTS_PER_PAGE)

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
            "all_skills": Skill.objects.all(),
            "active_skill": active_skill,
        },
    )


def project_page(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def create_project(request):
    form = ProjectForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": False},
        )

    project = form.save(commit=False)
    project.owner = request.user
    project.save()
    project.participants.add(request.user)
    return redirect("projects:detail", project_pk=project.pk)


@login_required
def edit_project(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    form = ProjectForm(request.POST or None, instance=project)
    if not form.is_valid():
        return render(
            request,
            "projects/create-project.html",
            {"form": form, "is_edit": True},
        )

    project = form.save()
    return redirect("projects:detail", project_pk=project.pk)


@login_required
@require_POST
def finish_project(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    if project.owner != request.user:
        return JsonResponse(
            {"status": "error", "error": "Завершить проект может только автор."},
            status=HTTP_BAD_REQUEST,
        )
    if project.status != Project.STATUS_OPEN:
        return JsonResponse(
            {"status": "error", "error": "Проект уже закрыт."},
            status=HTTP_BAD_REQUEST,
        )

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_my_participation(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk)
    participant = project.participants.filter(pk=request.user.pk).exists()
    if participant:
        project.participants.remove(request.user)
    else:
        project.participants.add(request.user)

    return JsonResponse({"status": "ok", "participant": not participant})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.all()
    if query:
        skills = skills.filter(name__istartswith=query)
    skills = list(skills.values("id", "name")[:SUGGESTIONS_LIMIT])
    return JsonResponse(skills, safe=False)


@login_required
@require_POST
def attach_project_skill(request, project_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        payload = {}

    skill_id = payload.get("skill_id")
    name = payload.get("name", "")
    if name is None:
        name = ""
    name = name.strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse(
            {"error": "Укажите идентификатор или название навыка."},
            status=HTTP_BAD_REQUEST,
        )

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.pk,
            "id": skill.pk,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def detach_project_skill(request, project_pk, skill_pk):
    project = get_object_or_404(Project, pk=project_pk, owner=request.user)
    skill = get_object_or_404(Skill, pk=skill_pk, projects=project)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
