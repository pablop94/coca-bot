# Generated by Django 4.0.2 on 2022-02-13 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Skip",
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
            ],
        ),
    ]
