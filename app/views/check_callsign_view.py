from datetime import date
import re

from django.shortcuts import render
from django.utils.translation import gettext as _

from app.models import Callsign, License


def check_callsign(request):
    context = {
        "title": _("Strona Główna"),
        "is_active": False,
        "is_empty": False,
    }
    callsign = request.GET.get("callsign")

    if callsign is None:
        return render(request, "check_callsign.html", context)

    callsign = re.sub(r"[\s-]+", "", callsign.upper())

    if len(callsign) < 4 or len(callsign) > 7:
        context["error"] = _(
            "Znak ma nieprawidłową długość. Musi mieć od 4 do 7 znaków."
        )
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)
    if not re.fullmatch(
        r"^(SP|SQ|SN|SO|3Z|HF|SR){1}[0-9]{1}[A-Z0-9]{1,4}$", callsign
    ):
        context["error"] = _("To nie jest poprawny polski znak krótkofalarski.")
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)

    db_callsign = Callsign.objects.filter(callsign=callsign).first()
    if db_callsign is None:
        context["is_empty"] = True
    else:
        newest_license = (
            License.objects.filter(assigned_callsign=db_callsign)
            .order_by("-expiration_date")
            .first()
        )
        if newest_license is None:
            context["is_empty"] = True
        elif newest_license.expiration_date >= date.today():
            context["is_active"] = True

    prefix = callsign[:2]
    digit = int(callsign[2:3])
    suffix = callsign[3:]

    if prefix in ["SP", "SQ"]:
        context["prefix_recommendation"] = "sp-sq"
    elif prefix in ["SN", "SO"]:
        context["prefix_recommendation"] = "sn-so"
    elif prefix in ["HF", "3Z"]:
        context["prefix_recommendation"] = "hf-3z"
    elif prefix in ["SR"]:
        context["prefix_recommendation"] = "sr"

    if digit == 0:
        context["digit_recommendation"] = "0"
    else:
        context["digit_recommendation"] = str(digit)

    context["remarks"] = []

    if len(suffix) == 4:
        context["remarks"].append("aprsn't")

    if prefix == "HF" and digit == 0:
        context["remarks"].append("hf0")

    context["report"] = True
    context["callsign"] = callsign
    return render(request, "check_callsign.html", context)
