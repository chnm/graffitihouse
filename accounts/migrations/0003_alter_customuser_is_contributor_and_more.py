# Generated by Django 4.1.7 on 2023-03-29 19:59

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0002_alter_customuser_is_contributor_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="is_contributor",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_staff",
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_student",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="customuser",
            name="is_volunteer",
            field=models.BooleanField(default=False),
        ),
    ]
