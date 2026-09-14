from django.contrib.auth.management import create_permissions
from django.db import migrations

CONTENT_APPS = ("graffiti", "people", "source")
ROLES = {
    "Students": ("add", "change", "view"),
    "Volunteers": ("add", "change", "view"),
    "Contributors": ("add", "change", "delete", "view"),
}


def create_groups(apps, schema_editor):
    # Permissions are normally created post-migrate; force them now.
    for app_config in apps.get_app_configs():
        if app_config.label in CONTENT_APPS:
            app_config.models_module = True
            create_permissions(app_config, apps=apps, verbosity=0)
            app_config.models_module = None

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    for name, actions in ROLES.items():
        group, _ = Group.objects.get_or_create(name=name)
        group.permissions.set(
            Permission.objects.filter(
                content_type__app_label__in=CONTENT_APPS,
                codename__regex=rf"^({'|'.join(actions)})_",
            )
        )


def delete_groups(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name__in=ROLES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_drop_role_flags"),
        ("graffiti", "0014_created_by"),
        ("people", "0005_created_by"),
        ("source", "0005_created_by"),
    ]

    operations = [migrations.RunPython(create_groups, delete_groups)]
