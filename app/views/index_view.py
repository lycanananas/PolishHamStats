from django.shortcuts import render
from django.utils.translation import gettext as _

def index(request):
    return render(request, "index.html", {"title": _("Strona Główna")})

def about(request):
    return render(request, "about.html", {"title": _("O projekcie")})