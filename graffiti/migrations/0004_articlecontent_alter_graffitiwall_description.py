# Generated by Django 4.1.7 on 2023-03-29 19:41

import django.db.models.deletion
import prose.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("graffiti", "0003_alter_ancillarysource_access_rights_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticleContent",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", prose.fields.DocumentContentField()),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AlterField(
            model_name="graffitiwall",
            name="description",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.articlecontent",
            ),
        ),
    ]
