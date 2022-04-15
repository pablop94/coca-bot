# Generated by Django 4.0.3 on 2022-04-11 04:58

from django.db import migrations


def set_birthdays(apps, schema_editor):
    Participant = apps.get_model("meals", "Participant")

    birthdays = {
        "pablo": "1994-06-14",
        "juli": "1994-04-09",
        "cele": "1995-05-28",
        "fantas": "1993-07-30",
        "euge": "1989-12-22",
    }

    participants = Participant.objects.filter(name__in=birthdays.keys())
    updated_participants = []
    for participant in participants:
        participant.birthday = birthdays[participant.name]
        updated_participants.append(participant)

    Participant.objects.bulk_update(updated_participants, ["birthday"])


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0009_participant_birthday"),
    ]

    operations = [migrations.RunPython(set_birthdays, migrations.RunPython.noop)]
