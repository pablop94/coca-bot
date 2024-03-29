# Generated by Django 4.0.3 on 2022-05-31 23:00

from django.db import migrations


def create_coca_setting(apps, schema_editor):
    CocaSettings = apps.get_model("meals", "CocaSettings")

    CocaSettings.objects.create(
        reminder_hour_utc=14,
        reminder_day=0,
        history_resume_day=1,
        random_run_probability=50,
    )


def delete_coca_setting(apps, schema_editor):
    CocaSettings = apps.get_model("meals", "CocaSettings")

    CocaSettings.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0011_cocasettings"),
    ]

    operations = [migrations.RunPython(create_coca_setting, delete_coca_setting)]
