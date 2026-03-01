import re
from base64 import urlsafe_b64decode
from collections import defaultdict
from datetime import date

from django.shortcuts import render
from django.core.paginator import Paginator
from django.utils.translation import gettext as _

from app.models import Callsign, License

VALID_PREFIXES = ("SP", "SQ", "SO", "SN", "HF", "3Z", "SR")
VALID_DIGITS = tuple(str(index) for index in range(10))


def _clean_selected_values(raw_values: str | None, valid_values: tuple[str, ...]) -> list[str]:
    if raw_values is None:
        return list(valid_values)

    selected_values = [value for value in raw_values.split("|") if value in valid_values]
    return selected_values or list(valid_values)


def _build_basic_regex(prefixes: str | None, digits: str | None, suffix: str | None) -> str:
    selected_prefixes = _clean_selected_values(prefixes, VALID_PREFIXES)
    selected_digits = _clean_selected_values(digits, VALID_DIGITS)
    escaped_suffix = re.escape(suffix or "")
    return f"^({'|'.join(selected_prefixes)})({'|'.join(selected_digits)}){escaped_suffix}"


def _decode_regex_query(encoded_regex: str | None) -> str:
    if not encoded_regex:
        raise ValueError("Missing encoded regex")
    return urlsafe_b64decode(encoded_regex).decode()


def callsign_page(request):
    context = {
        "title": _("Lista znaków"),
        "callsigns": [],
        "is_filter_error": False,
    }

    try:
        filter_type = request.GET.get("filter_type")
        if filter_type == "basic":
            regex = _build_basic_regex(
                prefixes=request.GET.get("prefixes"),
                digits=request.GET.get("digits"),
                suffix=request.GET.get("suffix"),
            )
            callsigns = Callsign.objects.filter(callsign__iregex=regex)
        elif filter_type == "regex":
            regex = _decode_regex_query(request.GET.get("regex"))
            callsigns = Callsign.objects.filter(callsign__iregex=regex)
        else:
            callsigns = Callsign.objects.all()
    except Exception:
        context["is_filter_error"] = True
        callsigns = Callsign.objects.all()

    paginator = Paginator(callsigns, 50)
    page_number = request.GET.get("page")

    try:
        page = paginator.get_page(page_number)
    except Exception:
        context["is_filter_error"] = True
        callsigns = Callsign.objects.all()
        paginator = Paginator(callsigns, 50)
        page = paginator.get_page(page_number)
        
    context["page_object"] = page
    context["callsign_count"] = paginator.count

    page_callsigns = list(context["page_object"].object_list)
    callsign_ids = [callsign.id for callsign in page_callsigns]

    licenses_by_callsign = defaultdict(list)
    if callsign_ids:
        licenses = (
            License.objects.filter(assigned_callsign_id__in=callsign_ids)
            .order_by("assigned_callsign_id", "-expiration_date")
            .all()
        )
        for license in licenses:
            licenses_by_callsign[license.assigned_callsign_id].append(license)

    for callsign in page_callsigns:
        context_callsign = {
            "callsign": callsign.callsign,
            "licenses": [],
            "is_active": False,
        }

        db_licenses_query = licenses_by_callsign.get(callsign.id, [])
        if len(db_licenses_query) == 0:
            context_callsign_license = {
                "license": "--",
                "license_slug": "--",
            }
            context_callsign["licenses"].append(context_callsign_license)
            context["callsigns"].append(context_callsign)
            continue
        newest_license = db_licenses_query[0]
        for license in db_licenses_query:
            context_callsign_license = {
                "license": license.license,
                "license_slug": license.license.replace("/", "-"),
            }
            context_callsign["licenses"].append(context_callsign_license)
        context["callsigns"].append(context_callsign)

        context_callsign["expiration_date"] = newest_license.expiration_date
        context_callsign["power"] = newest_license.power
        context_callsign["category"] = newest_license.category
        context_callsign["type"] = newest_license.type
        if newest_license.expiration_date >= date.today():
            context_callsign["is_active"] = True

    return render(request, "callsign_page.html", context)
