# Generated by Django 4.1.5 on 2023-01-18 01:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rooms", "0002_room_description_alter_amenity_description"),
    ]

    operations = [
        migrations.AddField(
            model_name="room",
            name="name",
            field=models.CharField(default="", max_length=180),
        ),
    ]
