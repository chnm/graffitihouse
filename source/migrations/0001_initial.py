# Generated by Django 5.1.2 on 2025-01-24 18:53

import django.db.models.deletion
import taggit_selectize.managers
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("graffiti", "0008_remove_ancillarysource_archive_and_more"),
        ("people", "0001_initial"),
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="Archive",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.location",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AncillarySource",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=100)),
                ("image", models.ImageField(null=True, upload_to="images/")),
                (
                    "item_type",
                    models.CharField(
                        choices=[
                            ("image", "Image"),
                            ("newsprint", "Newsprint"),
                            ("wall", "Wall"),
                            ("letter", "Letter"),
                            ("photograph", "Photograph"),
                            ("drawing", "Drawing"),
                            ("artwork", "Artwork"),
                            ("game", "Game"),
                            ("poem", "Poem"),
                            ("other", "Other"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "creator",
                    models.CharField(
                        blank=True,
                        help_text="An entity primarily responsible for making the resource.",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "contributor",
                    models.CharField(
                        blank=True,
                        help_text="An entity responsible for making contributions to the resource.",
                        max_length=100,
                        null=True,
                    ),
                ),
                (
                    "date",
                    models.CharField(
                        blank=True,
                        help_text="The date of the source, if known.",
                        max_length=100,
                        null=True,
                    ),
                ),
                ("language", models.CharField(blank=True, max_length=100, null=True)),
                ("box", models.CharField(blank=True, max_length=225, null=True)),
                ("folder", models.CharField(blank=True, max_length=225, null=True)),
                (
                    "access_rights",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("latitude", models.FloatField(blank=True, null=True)),
                ("longitude", models.FloatField(blank=True, null=True)),
                ("transcription", models.TextField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "graffiti_id",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.graffitiwall",
                    ),
                ),
                (
                    "location",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.location",
                    ),
                ),
                (
                    "site",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.site",
                    ),
                ),
                (
                    "tags",
                    taggit_selectize.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
                (
                    "archive",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="source.archive",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DocumentPersonRole",
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
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("SENDER", "Sender"),
                            ("RECIPIENT", "Recipient"),
                            ("GRANTEE", "Grantee"),
                            ("GRANTOR", "Grantor"),
                        ],
                        max_length=100,
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="source.ancillarysource",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="people.person"
                    ),
                ),
            ],
            options={
                "verbose_name": "People",
                "verbose_name_plural": "People",
            },
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="people",
            field=models.ManyToManyField(
                through="source.DocumentPersonRole", to="people.person"
            ),
        ),
        migrations.AddIndex(
            model_name="documentpersonrole",
            index=models.Index(
                fields=["person", "document", "role"],
                name="source_docu_person__ef312d_idx",
            ),
        ),
    ]
