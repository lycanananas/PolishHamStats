from django.urls import path

from .views import (
    callsign_view,
    license_view,
    index_view,
    proxy_view,
    license_page_view,
    callsign_page_view,
    soon_expire_view,
    check_callsign_view,
)

urlpatterns = [
    path("", index_view.index, name="index"),
    path("about", index_view.about, name="index"),
    path("callsign/<callsign>", callsign_view.callsign, name="callsign"),
    path("pzk_proxy/<callsign>", proxy_view.proxy, name="proxy_pzk"),
    path("license/<license>", license_view.license, name="license"),
    path("licenses", license_page_view.license_page, name="licenses"),
    path("callsigns", callsign_page_view.callsign_page, name="callsigns"),
    path("soonexpire", soon_expire_view.soon_expire, name="soon_expire"),
    path("checkcallsign", check_callsign_view.check_callsign, name="check_callsign"),
]
