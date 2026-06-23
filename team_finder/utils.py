from django.core.paginator import Paginator


def get_page_obj(request, object_list, per_page):
    paginator = Paginator(object_list, per_page)
    return paginator.get_page(request.GET.get("page"))
