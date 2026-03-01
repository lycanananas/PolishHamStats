from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0003_model_constraints_and_indexes"),
    ]

    operations = [
        migrations.CreateModel(
            name="PzkCache",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("callsign", models.CharField(max_length=32, unique=True)),
                ("payload", models.JSONField(default=dict)),
                ("fetched_at", models.DateTimeField()),
                ("expires_at", models.DateTimeField()),
            ],
        ),
        migrations.AddIndex(
            model_name="pzkcache",
            index=models.Index(fields=["expires_at"], name="app_pzkcach_expires_4e4f11_idx"),
        ),
    ]
