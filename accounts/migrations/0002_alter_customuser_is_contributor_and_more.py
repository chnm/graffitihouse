# Generated by Django 4.1.7 on 2023-03-21 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_contributor',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_staff',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_student',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_volunteer',
            field=models.BooleanField(),
        ),
    ]
