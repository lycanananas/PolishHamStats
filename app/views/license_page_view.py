from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext as _

from app.models import License


def license_page(request):
    licenses = License.objects.select_related("assigned_callsign").order_by("license")
    paginator = Paginator(licenses, 50)
    page_number = request.GET.get("page")

    return render(
        request,
        "license_page.html",
        {
            "title": _("Lista pozwoleń"),
            "page_object": paginator.get_page(page_number),
            "license_count": paginator.count,
        },
    )
