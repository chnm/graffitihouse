import re

from django.db import migrations
from django.utils.html import linebreaks

HTML_TAG = re.compile(r"</?[a-zA-Z][^>]*>")


def plain_text_descriptions_to_html(apps, schema_editor):
    """Convert descriptions saved as plain text by the crop tool to HTML.

    Descriptions entered through the admin's rich-text editor are already HTML
    and are left alone.
    """
    GraffitiPhoto = apps.get_model("graffiti", "GraffitiPhoto")
    for photo in GraffitiPhoto.objects.exclude(description__isnull=True).exclude(
        description=""
    ):
        if HTML_TAG.search(photo.description):
            continue
        # RichTextField bleach-cleans on save, so stored text is already escaped.
        text = photo.description.strip()
        photo.description = linebreaks(text) if text else ""
        photo.save(update_fields=["description"])


class Migration(migrations.Migration):
    dependencies = [
        ("graffiti", "0015_remove_drawing_graffiti_type"),
    ]

    operations = [
        migrations.RunPython(
            plain_text_descriptions_to_html, migrations.RunPython.noop
        ),
    ]
