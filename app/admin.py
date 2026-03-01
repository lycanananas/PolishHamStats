from django.contrib import admin
from .models import Callsign, License


class LicenseInline(admin.TabularInline):
    model = License
    fk_name = "assigned_callsign"
    fields = ("license", "category", "type", "expiration_date", "last_seen")
    extra = 0
    show_change_link = True


@admin.register(Callsign)
class CallsignAdmin(admin.ModelAdmin):
	list_display = ("callsign", "first_seen", "last_seen", "licenses_count")
	search_fields = ("callsign",)
	ordering = ("callsign",)
	inlines = [LicenseInline]

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		return queryset.prefetch_related("license_set")

	@admin.display(description="Liczba licencji")
	def licenses_count(self, obj):
		return obj.license_set.count()


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
	list_display = (
		"license",
		"assigned_callsign",
		"category",
		"type",
		"expiration_date",
		"last_seen",
	)
	search_fields = ("license", "assigned_callsign__callsign")
	list_filter = ("category", "type")
	ordering = ("license",)
