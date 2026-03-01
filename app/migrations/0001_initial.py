import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Callsign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('callsign', models.CharField(max_length=32)),
                ('first_seen', models.DateField()),
                ('last_seen', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='License',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('license', models.CharField(max_length=255)),
                ('category', models.IntegerField(choices=[(0, 'Invalid'), (1, 'Kategoria 1'), (2, 'Kategoria 2'), (3, 'Kategoria 3'), (4, 'Kategoria 4'), (5, 'Kategoria 5'), (-1, 'Kategoria Dodatkowa')])),
                ('expiration_date', models.DateField()),
                ('first_seen', models.DateField()),
                ('last_seen', models.DateField()),
                ('assigned_callsign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.callsign')),
            ],
        ),
    ]
