# Generated by Django 4.0.3 on 2022-04-01 03:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0007_meals_to_meal_items"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="meal",
            name="description",
        ),
        migrations.RemoveField(
            model_name="meal",
            name="meal_owner",
        ),
    ]
