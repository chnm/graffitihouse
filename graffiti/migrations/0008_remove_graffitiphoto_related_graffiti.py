# Generated by Django 5.1.2 on 2024-10-31 20:45

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("graffiti", "0007_graffitiphoto_coordinates"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="graffitiphoto",
            name="related_graffiti",
        ),
    ]