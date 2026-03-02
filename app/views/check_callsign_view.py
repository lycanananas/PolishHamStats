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

    if len(callsign) < 4 or len(callsign) > 10:
        context["error"] = _(
            "Znak ma nieprawidłową długość. Musi mieć od 4 do 10 znaków."
        )
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)

    parsed_callsign = re.fullmatch(
        r"^(HF|SN|SO|SP|SQ|SR|3Z)([0-9])([A-Z0-9]+)$", callsign
    )
    if parsed_callsign is None:
        context["error"] = _("To nie jest poprawny polski znak krótkofalarski.")
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)

    prefix, digit_text, suffix = parsed_callsign.groups()

    if not suffix[-1].isalpha():
        context["error"] = _(
            "To nie jest poprawny polski znak krótkofalarski. Ostatni znak suffixu musi być literą."
        )
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)

    if prefix == "SR" and len(suffix) > 4:
        context["error"] = _(
            "Prefix SR nie obsługuje wydłużonego suffixu. Dla SR maksymalna długość suffixu to 4 znaki."
        )
        context["callsign"] = callsign
        return render(request, "check_callsign.html", context)

    if prefix != "SR" and len(suffix) > 7:
        context["error"] = _(
            "To nie jest poprawny polski znak krótkofalarski. Maksymalna długość suffixu to 7 znaków."
        )
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

    digit = int(digit_text)

    if prefix in ["SP", "SQ"]:
        context["prefix_recommendation"] = "sp-sq"
    elif prefix in ["SN", "SO"]:
        context["prefix_recommendation"] = "sn-so"
    elif prefix in ["HF", "3Z"]:
        context["prefix_recommendation"] = "hf-3z"
    elif prefix == "SR":
        context["prefix_recommendation"] = "sr"

    if digit == 0:
        context["digit_recommendation"] = "0"
    else:
        context["digit_recommendation"] = str(digit)

    context["remarks"] = []

    if len(suffix) == 1:
        context["remarks"].append("single-letter-suffix")
        context["single_letter_suffix_variants_all_districts"] = 7 * 10 * 26
        context["single_letter_suffix_variants_without_zero"] = 7 * 9 * 26

    if len(suffix) > 4:
        context["remarks"].append("additional-permit-length")

    if len(suffix) >= 4:
        context["remarks"].append("aprs-ax25-limit")
        context["remarks"].append("ft8-nonstandard")

    if any(char.isdigit() for char in suffix):
        context["remarks"].append("suffix-digit")
        context["remarks"].append("ft8-nonstandard")

    if prefix == "HF" and digit == 0:
        context["remarks"].append("hf0")

    context["remarks"] = list(dict.fromkeys(context["remarks"]))

    context["report"] = True
    context["callsign"] = callsign
    return render(request, "check_callsign.html", context)
