# Generated by Django 4.0.2 on 2022-03-14 00:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meals", "0004_meal_done_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="meal",
            name="done_at",
            field=models.DateField(null=True),
        ),
    ]
