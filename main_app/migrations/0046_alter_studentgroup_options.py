# Generated by Django 4.1.1 on 2023-09-19 20:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("main_app", "0045_studentgroup_student_student_group"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="studentgroup",
            options={
                "verbose_name": "مجموعة الطلاب",
                "verbose_name_plural": "مجموعات الطلاب",
            },
        ),
    ]
