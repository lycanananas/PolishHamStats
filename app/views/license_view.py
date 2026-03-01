from django.shortcuts import render

from app.models import License
from app.views.license_context import is_license_active, serialize_license

def license(request, license):
    normalized_license = license.replace("-", "/")
    
    db_license = License.objects.select_related("assigned_callsign").filter(
        license=normalized_license
    ).first()
    if db_license is None:
        return render(
            request,
            "license.html",
            {
                "title": normalized_license,
                "license": normalized_license,
            },
        )

    license_data = serialize_license(db_license)

    return render(
        request,
        "license.html",
        {
            "title": normalized_license,
            "license": normalized_license,
            "is_active": is_license_active(db_license),
            "callsign": db_license.assigned_callsign.callsign,
            "current_license": license_data,
        },
    )
