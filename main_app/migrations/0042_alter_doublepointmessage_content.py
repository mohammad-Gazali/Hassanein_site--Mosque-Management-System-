# Generated by Django 4.1.1 on 2023-09-07 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0041_alter_memorizemessage_first_info_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="doublepointmessage",
            name="content",
            field=models.JSONField(
                default=dict, null=True, verbose_name="التسميع الذي تم مضاعفته"
            ),
        ),
    ]