import os

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def image_path(image_field):
    """
    Creates a reliable path to an image, handling various path issues.
    Usage: {% image_path object.image %}
    """
    if not image_field or not hasattr(image_field, "name") or not image_field.name:
        return ""

    # First try - direct path
    image_path = image_field.name

    # Remove any double 'images/' in the path
    if "images/images/" in image_path:
        image_path = image_path.replace("images/images/", "images/")

    # Ensure path starts with a slash
    if not image_path.startswith("/"):
        image_path = "/" + image_path

    return image_path
