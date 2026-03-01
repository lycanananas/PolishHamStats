from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='license',
            name='applicant_city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='applicant_house',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='applicant_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='applicant_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='applicant_street',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='emission',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='enduser_city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='enduser_house',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='enduser_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='enduser_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='enduser_street',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='input_frequency',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='lat',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='lng',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='name_type_station',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='output_frequency',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='power',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='station_city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='station_house',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='station_location',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='station_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='station_street',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='license',
            name='type',
            field=models.IntegerField(choices=[(0, 'Invalid'), (1, 'Individual'), (2, 'Individual Device'), (3, 'Club'), (4, 'Club Device')], default=1),
        ),
    ]
