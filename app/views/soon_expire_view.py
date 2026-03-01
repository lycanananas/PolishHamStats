from django.shortcuts import render
from django.utils.translation import gettext as _
from datetime import date, timedelta
from django.db.models import OuterRef, Subquery, F
from django.core.paginator import Paginator

from app.models import License


DEFAULT_SOON_EXPIRE_DAYS = 30
DEFAULT_SOON_EXPIRE_PER_PAGE = 50


def _parse_days(raw_days):
    try:
        days = int(raw_days)
    except (TypeError, ValueError):
        return DEFAULT_SOON_EXPIRE_DAYS

    if days < 1:
        return DEFAULT_SOON_EXPIRE_DAYS

    return min(days, 3650)


def soon_expire(request):
    days = _parse_days(request.GET.get("days"))
    today = date.today()
    max_expiration_day = today + timedelta(days=days)

    latest_expiration_subquery = (
        License.objects.filter(assigned_callsign=OuterRef("assigned_callsign"))
        .order_by("-expiration_date")
        .values("expiration_date")[:1]
    )

    db_licenses_query = (
        License.objects.select_related("assigned_callsign")
        .annotate(latest_expiration=Subquery(latest_expiration_subquery))
        .filter(
            expiration_date=F("latest_expiration"),
            latest_expiration__gte=today,
            latest_expiration__lte=max_expiration_day,
        )
        .order_by("expiration_date")
    )

    paginator = Paginator(db_licenses_query, DEFAULT_SOON_EXPIRE_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    callsigns = [
        {
            "license": db_license.license,
            "license_slug": db_license.license.replace("/", "-"),
            "category": License.CATEGORY_MAP[db_license.category],
            "callsign": db_license.assigned_callsign.callsign,
            "power": db_license.power,
            "expiration_date": db_license.expiration_date,
            "type": License.TYPE_MAP[db_license.type],
        }
        for db_license in page_obj.object_list
    ]

    return render(
        request,
        "soon_expire.html",
        {
            "title": _("Niedługo wygasną"),
            "days": days,
            "callsigns": callsigns,
            "callsign_count": paginator.count,
            "page_obj": page_obj,
        },
    )
