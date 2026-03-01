from django.shortcuts import render
from django.http import Http404
from django.utils.translation import gettext as _

from app.models import Callsign, License
from app.views.license_context import is_license_active, serialize_license


def callsign(request, callsign):
    normalized_callsign = callsign.upper()

    db_callsign = Callsign.objects.filter(callsign=normalized_callsign).first()
    if db_callsign is None:
        return render(
            request,
            "callsign.html",
            {
                "title": normalized_callsign,
                "callsign": normalized_callsign,
            },
        )

    db_licenses_query = list(
        License.objects.filter(assigned_callsign=db_callsign).order_by("-expiration_date")
    )
    if not db_licenses_query:
        raise Http404(_("Znak nie ma żadnego pozwolenia! Skontaktuj się z autorami!"))

    newest_license = db_licenses_query[0]
    serialized_licenses = [serialize_license(db_license) for db_license in db_licenses_query]

    return render(
        request,
        "callsign.html",
        {
            "title": db_callsign.callsign,
            "callsign": db_callsign.callsign,
            "first_seen": db_callsign.first_seen,
            "last_seen": db_callsign.last_seen,
            "licenses": serialized_licenses,
            "current_license": serialized_licenses[0],
            "is_active": is_license_active(newest_license),
        },
    )
