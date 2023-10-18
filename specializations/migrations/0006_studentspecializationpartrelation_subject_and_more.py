# Generated by Django 4.2.6 on 2023-10-18 16:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0052_awqafnoqstudentrelation_points_and_more'),
        ('specializations', '0005_part_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentSpecializationPartRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_old', models.BooleanField(default=False)),
                ('points', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='الاسم')),
                ('specialization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specializations.specialization', verbose_name='الاختصاص')),
            ],
            options={
                'verbose_name': 'مقرر',
                'verbose_name_plural': 'المقررات',
            },
        ),
        migrations.RemoveField(
            model_name='part',
            name='level',
        ),
        migrations.RemoveField(
            model_name='part',
            name='students',
        ),
        migrations.DeleteModel(
            name='Level',
        ),
        migrations.AddField(
            model_name='studentspecializationpartrelation',
            name='part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='specializations.part'),
        ),
        migrations.AddField(
            model_name='studentspecializationpartrelation',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main_app.student'),
        ),
        migrations.AddField(
            model_name='part',
            name='subject',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='specializations.subject', verbose_name='المقرر'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='studentspecializationpartrelation',
            unique_together={('part', 'student')},
        ),
    ]
