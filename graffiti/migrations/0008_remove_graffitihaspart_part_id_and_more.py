# Generated by Django 4.0.9 on 2023-03-10 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('graffiti', '0007_archive_box_archive_folder'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='graffitihaspart',
            name='part_id',
        ),
        migrations.AlterField(
            model_name='graffitihaspart',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]