# Generated by Django 4.2.6 on 2023-10-18 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0051_rename_master_name_coming_master_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='awqafnoqstudentrelation',
            name='points',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='awqafnoqstudentrelation',
            name='is_old',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='awqafnoqstudentrelation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.student'),
        ),
        migrations.AlterField(
            model_name='awqafnoqstudentrelation',
            name='test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.awqaftestnoq'),
        ),
        migrations.AlterUniqueTogether(
            name='awqafnoqstudentrelation',
            unique_together={('test', 'student')},
        ),
    ]