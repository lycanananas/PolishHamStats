from django.db import models


class Callsign(models.Model):
    callsign = models.CharField(max_length=32, unique=True)
    first_seen = models.DateField()
    last_seen = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=["last_seen"]),
        ]

    def __str__(self):
        return self.callsign


class License(models.Model):
    class Category(models.IntegerChoices):
        INVALID = 0
        KATEGORIA_1 = 1
        KATEGORIA_2 = 2
        KATEGORIA_3 = 3
        KATEGORIA_4 = 4
        KATEGORIA_5 = 5
        KATEGORIA_DODATKOWA = -1

    CATEGORY_MAP = {
        Category.INVALID: "Nie poprawna kategoria!",
        Category.KATEGORIA_1: "Kategoria 1",
        Category.KATEGORIA_2: "Kategoria 2 (Nie wydawany typ!!)",
        Category.KATEGORIA_3: "Kategoria 3",
        Category.KATEGORIA_4: "Kategoria 4 (Nie wydawany typ!!)",
        Category.KATEGORIA_5: "Kategoria 5 - Stacja Automatyczna",
        Category.KATEGORIA_DODATKOWA: "Pozwolenie dodatkowe",
    }

    class Type(models.IntegerChoices):
        INVALID = 0
        INDIVIDUAL = 1
        INDIVIDUAL_DEVICE = 2
        CLUB = 3
        CLUB_DEVICE = 4

    TYPE_MAP = {
        Type.INVALID: "Nie poprawna typ!",
        Type.INDIVIDUAL: "Indywidualne",
        Type.INDIVIDUAL_DEVICE: "Indywidualne - Stacja automatyczna",
        Type.CLUB: "Klubowe",
        Type.CLUB_DEVICE: "Klubowe - Stacja automatyczna",
    }
    
    license = models.CharField(max_length=255, unique=True)
    category = models.IntegerField(choices=Category)
    assigned_callsign = models.ForeignKey(Callsign, on_delete=models.CASCADE)
    expiration_date = models.DateField()
    first_seen = models.DateField()
    last_seen = models.DateField()
    power = models.IntegerField(null=True)
    type = models.IntegerField(choices=Type, default=Type.INDIVIDUAL)
    station_location = models.CharField(max_length=255, null=True)
    applicant_name = models.CharField(max_length=255, null=True)
    applicant_city = models.CharField(max_length=255, null=True)
    applicant_street = models.CharField(max_length=255, null=True)
    applicant_house = models.CharField(max_length=255, null=True)
    applicant_number = models.CharField(max_length=255, null=True)
    enduser_name = models.CharField(max_length=255, null=True)
    enduser_city = models.CharField(max_length=255, null=True)
    enduser_street = models.CharField(max_length=255, null=True)
    enduser_house = models.CharField(max_length=255, null=True)
    enduser_number = models.CharField(max_length=255, null=True)
    station_city = models.CharField(max_length=255, null=True)
    station_street = models.CharField(max_length=255, null=True)
    station_house = models.CharField(max_length=255, null=True)
    station_number = models.CharField(max_length=255, null=True)
    lat = models.FloatField(null=True)
    lng = models.FloatField(null=True)
    name_type_station = models.CharField(max_length=255, null=True)
    emission = models.CharField(max_length=255, null=True)
    input_frequency = models.CharField(max_length=255, null=True)
    output_frequency = models.CharField(max_length=255, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["expiration_date"]),
            models.Index(fields=["last_seen"]),
            models.Index(fields=["assigned_callsign", "expiration_date"]),
        ]

    def __str__(self):
        return self.license


class PzkCache(models.Model):
    callsign = models.CharField(max_length=32, unique=True)
    payload = models.JSONField(default=dict)
    fetched_at = models.DateTimeField()
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return self.callsign
