# Generated by Django 4.1.1 on 2023-08-29 15:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0036_delete_pointsdeleting_delete_pointsdeletingcause"),
    ]

    operations = [
        migrations.AlterField(
            model_name="student",
            name="mother_name",
            field=models.CharField(
                blank=True, max_length=255, null=True, verbose_name="اسم الأم"
            ),
        ),
    ]