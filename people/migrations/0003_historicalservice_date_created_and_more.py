# Generated by Django 5.1.2 on 2025-02-20 21:24

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("people", "0002_historicalalias_historicalorganization_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="historicalservice",
            name="date_created",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalservice",
            name="date_updated",
            field=models.DateTimeField(
                blank=True, default=django.utils.timezone.now, editable=False
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="historicalservice",
            name="military_division",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="historicalservice",
            name="military_governance",
            field=models.CharField(
                blank=True,
                choices=[("union", "Union"), ("confederacy", "Confederacy")],
                max_length=11,
            ),
        ),
        migrations.AddField(
            model_name="service",
            name="date_created",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="service",
            name="date_updated",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="service",
            name="military_division",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="service",
            name="military_governance",
            field=models.CharField(
                blank=True,
                choices=[("union", "Union"), ("confederacy", "Confederacy")],
                max_length=11,
            ),
        ),
        migrations.AlterField(
            model_name="historicalservice",
            name="military_branch",
            field=models.CharField(
                blank=True,
                choices=[
                    ("army", "Army"),
                    ("navy", "Navy"),
                    ("cavalry", "Cavalry"),
                    ("coastguard", "Coast Guard"),
                ],
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="service",
            name="military_branch",
            field=models.CharField(
                blank=True,
                choices=[
                    ("army", "Army"),
                    ("navy", "Navy"),
                    ("cavalry", "Cavalry"),
                    ("coastguard", "Coast Guard"),
                ],
                max_length=255,
            ),
        ),
    ]
