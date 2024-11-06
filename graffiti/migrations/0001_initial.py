# Generated by Django 4.1.7 on 2024-10-16 17:26

import django.db.models.deletion
import prose.fields
import taggit_selectize.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("taggit", "0005_auto_20220424_2025"),
    ]

    operations = [
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
                ("creator", models.CharField(blank=True, max_length=100, null=True)),
                ("description", models.TextField()),
                (
                    "contributor",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                ("date", models.CharField(blank=True, max_length=100, null=True)),
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
            ],
        ),
        migrations.CreateModel(
            name="GraffitiWall",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", prose.fields.RichTextField()),
                ("image", models.ImageField(upload_to="images/")),
                (
                    "room",
                    models.CharField(
                        help_text="Record the room name/number.", max_length=255
                    ),
                ),
                (
                    "spatial_position",
                    models.CharField(
                        help_text="Record the region code for this wall (e.g., B1, C3.",
                        max_length=100,
                    ),
                ),
                (
                    "identifier",
                    models.CharField(
                        help_text="Identifier refers to the number produced by the camera/phone. Please ensure these match.",
                        max_length=100,
                    ),
                ),
                (
                    "date_taken",
                    models.DateField(
                        help_text="Record the date the photograph was taken."
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("place", models.CharField(max_length=255)),
                ("address", models.CharField(max_length=255)),
                ("city", models.CharField(max_length=255)),
                ("state", models.CharField(max_length=255)),
                ("latitude", models.DecimalField(decimal_places=4, max_digits=9)),
                ("longitude", models.DecimalField(decimal_places=4, max_digits=9)),
            ],
            options={
                "verbose_name": "Location",
                "verbose_name_plural": "Locations",
                "ordering": ["state", "city", "place"],
            },
        ),
        migrations.CreateModel(
            name="WallRecordHistory",
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
                ("action", models.CharField(max_length=10)),
                ("data", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "photo_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="graffiti.graffitiwall",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "Wall Record Histories",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Site",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("image", models.ImageField(upload_to="images/")),
                ("date", models.CharField(max_length=100)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "location",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.location",
                    ),
                ),
                (
                    "tags",
                    taggit_selectize.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
                ("image", models.ImageField(upload_to="images/")),
                ("date_of_birth", models.DateTimeField(auto_now_add=True)),
                ("date_of_death", models.DateField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tags",
                    taggit_selectize.managers.TaggableManager(
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
            options={
                "verbose_name": "Person",
                "verbose_name_plural": "People",
            },
        ),
        migrations.AddField(
            model_name="graffitiwall",
            name="site_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.site",
                verbose_name="Site",
            ),
        ),
        migrations.AddField(
            model_name="graffitiwall",
            name="tags",
            field=taggit_selectize.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
        migrations.CreateModel(
            name="GraffitiPhoto",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(default="Name", max_length=100)),
                ("image", models.ImageField(null=True, upload_to="images/")),
                (
                    "identifier",
                    models.CharField(
                        max_length=100,
                        verbose_name="Identifier refers to the image filename.",
                    ),
                ),
                ("canvas", models.TextField(blank=True, null=True)),
                (
                    "canvas_coords",
                    models.TextField(blank=True, default="[]", null=True),
                ),
                (
                    "graffiti_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.graffitiwall",
                    ),
                ),
                (
                    "related_graffiti",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="related_graffiti",
                        to="graffiti.graffitiwall",
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
                        to="graffiti.ancillarysource",
                    ),
                ),
                (
                    "person",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="graffiti.person",
                    ),
                ),
            ],
            options={
                "verbose_name": "People",
                "verbose_name_plural": "People",
                "unique_together": {("person", "document", "role")},
            },
        ),
        migrations.CreateModel(
            name="Archive",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("description", models.TextField()),
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
        migrations.AddField(
            model_name="ancillarysource",
            name="archive",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.archive",
            ),
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="graffiti_id",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.graffitiwall",
            ),
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="location",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.location",
            ),
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="people",
            field=models.ManyToManyField(
                through="graffiti.DocumentPersonRole", to="graffiti.person"
            ),
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="site",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="graffiti.site",
            ),
        ),
        migrations.AddField(
            model_name="ancillarysource",
            name="tags",
            field=taggit_selectize.managers.TaggableManager(
                help_text="A comma-separated list of tags.",
                through="taggit.TaggedItem",
                to="taggit.Tag",
                verbose_name="Tags",
            ),
        ),
    ]
