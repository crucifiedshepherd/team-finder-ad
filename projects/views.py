import json

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import ProjectForm
from .models import Project, Skill

PROJECTS_PER_PAGE = 12
SUGGESTIONS_LIMIT = 10


def project_board(request):
    projects = Project.objects.select_related("owner").order_by("-created_at")
    active_skill = request.GET.get("skill")
    if active_skill:
        projects = projects.filter(skills__name=active_skill)

    paginator = Paginator(projects, PROJECTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "projects/project_list.html",
        {
            "projects": page_obj,
            "page_obj": page_obj,
            "all_skills": Skill.objects.order_by("name"),
            "active_skill": active_skill,
        },
    )


def project_page(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, "projects/project-details.html", {"project": project})


@login_required
def project_studio(request, pk=None):
    is_edit = pk is not None
    project = None
    if is_edit:
        project = get_object_or_404(Project, pk=pk, owner=request.user)

    if request.method == "POST":
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save(commit=False)
            if not is_edit:
                project.owner = request.user
            project.save()
            if not is_edit:
                project.participants.add(request.user)
            return redirect("projects:detail", pk=project.pk)
    else:
        form = ProjectForm(instance=project)

    return render(request, "projects/create-project.html", {"form": form, "is_edit": is_edit})


@login_required
@require_POST
def finish_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
        return JsonResponse({"status": "error"}, status=400)

    project.status = Project.STATUS_CLOSED
    project.save(update_fields=["status"])
    return JsonResponse({"status": "ok", "project_status": project.status})


@login_required
@require_POST
def toggle_my_participation(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if project.participants.filter(pk=request.user.pk).exists():
        project.participants.remove(request.user)
        participant = False
    else:
        project.participants.add(request.user)
        participant = True

    return JsonResponse({"status": "ok", "participant": participant})


@require_GET
def skill_suggestions(request):
    query = request.GET.get("q", "").strip()
    skills = Skill.objects.order_by("name")
    if query:
        skills = skills.filter(name__istartswith=query)
    skills = list(skills.values("id", "name")[:SUGGESTIONS_LIMIT])
    return JsonResponse(skills, safe=False)


@login_required
@require_POST
def attach_project_skill(request, pk):
    project = get_object_or_404(Project, pk=pk, owner=request.user)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        payload = {}

    skill_id = payload.get("skill_id")
    name = (payload.get("name") or "").strip()

    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif name:
        skill, created = Skill.objects.get_or_create(name=name)
    else:
        return JsonResponse({"error": "skill_id or name is required"}, status=400)

    added = not project.skills.filter(pk=skill.pk).exists()
    if added:
        project.skills.add(skill)

    return JsonResponse(
        {
            "skill_id": skill.id,
            "id": skill.id,
            "name": skill.name,
            "created": created,
            "added": added,
        }
    )


@login_required
@require_POST
def detach_project_skill(request, pk, skill_id):
    project = get_object_or_404(Project, pk=pk, owner=request.user)
    skill = get_object_or_404(Skill, pk=skill_id, projects=project)
    project.skills.remove(skill)
    return JsonResponse({"status": "ok"})
