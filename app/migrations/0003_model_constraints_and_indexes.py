from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_license_applicant_city_license_applicant_house_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="callsign",
            name="callsign",
            field=models.CharField(max_length=32, unique=True),
        ),
        migrations.AlterField(
            model_name="license",
            name="license",
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AddIndex(
            model_name="callsign",
            index=models.Index(fields=["last_seen"], name="app_callsig_last_se_2ff335_idx"),
        ),
        migrations.AddIndex(
            model_name="license",
            index=models.Index(fields=["expiration_date"], name="app_licens_expirat_0f1d96_idx"),
        ),
        migrations.AddIndex(
            model_name="license",
            index=models.Index(fields=["last_seen"], name="app_licens_last_se_25b69f_idx"),
        ),
        migrations.AddIndex(
            model_name="license",
            index=models.Index(
                fields=["assigned_callsign", "expiration_date"],
                name="app_licens_assigne_cfcd87_idx",
            ),
        ),
    ]
