from django.http import JsonResponse
from django.utils import timezone
from parsel import Selector
from datetime import timedelta

import requests

from app.models import PzkCache


def proxy(request, callsign):
    normalized_callsign = callsign.upper()
    now = timezone.now()
    cache = PzkCache.objects.filter(callsign=normalized_callsign).first()

    def extract_first(selector, xpath):
        value = selector.xpath(xpath).get()
        return value.strip() if value is not None else ""

    def extract_all(selector, xpath):
        values = [value.strip() for value in selector.xpath(xpath).getall()]
        return [value for value in values if value]

    def save_cache(payload):
        expires_at = now + timedelta(days=1)
        if cache is None:
            PzkCache.objects.create(
                callsign=normalized_callsign,
                payload=payload,
                fetched_at=now,
                expires_at=expires_at,
            )
            return

        cache.payload = payload
        cache.fetched_at = now
        cache.expires_at = expires_at
        cache.save(update_fields=["payload", "fetched_at", "expires_at"])

    if cache is not None and cache.expires_at > now:
        return JsonResponse(cache.payload)

    post_data = {
        "ec_view_members_znak_pokaz": normalized_callsign,
        "ec_view_members_action": "view_selected_members",
        "Submit": "Poka%BF",
    }
    try:
        pzk_request = requests.post(
            "https://pzk.org.pl/osec_ec_members_view.php", data=post_data, timeout=20
        )
        pzk_request.raise_for_status()
    except requests.RequestException:
        if cache is not None:
            return JsonResponse(cache.payload)
        return JsonResponse({"status": 502})

    selector = Selector(text=str(pzk_request.content, encoding="ISO 8859-2"))
    status = extract_first(
        selector,
        "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[4]/td[2]//text()",
    )

    if status != "":
        payload = {
            "status": 200,
            "znak": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[1]/td[2]//text()"),
            "status_stacji": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[2]/td[2]//text()"),
            "klasyfikacja": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[3]/td[2]//text()"),
            "ot": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[5]/td[2]//text()"),
            "rodzaj_stacji": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[6]/td[2]//text()"),
            "znak_poprzedni": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[7]/td[2]//text()"),
            "imie": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[8]/td[2]//text()"),
            "inne_znaki": extract_all(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[9]/td[2]//text()"),
            "ostatnia_aktulizacja": extract_first(selector, "/html/body/table/tr[4]/td/table[2]/tr/td/table/td[2]/table[2]/tr[10]/td[2]//text()"),
        }
    else:
        payload = {"status": 404}

    save_cache(payload)
    return JsonResponse(payload)
