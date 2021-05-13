# Generated by Django 2.2.10 on 2021-05-13 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Column',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('column_name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('file_name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('uploaded_time', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SmellType',
            fields=[
                ('smell_type', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('belonging_file', models.ManyToManyField(to='app.File')),
            ],
        ),
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('value', models.FloatField()),
                ('data_type', models.CharField(max_length=255)),
                ('belonging_smell', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.SmellType')),
            ],
        ),
        migrations.CreateModel(
            name='DetectedSmell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_smell_type', models.CharField(max_length=100)),
                ('total_element_count', models.IntegerField()),
                ('faulty_element_count', models.IntegerField()),
                ('faulty_list', models.CharField(max_length=1024)),
                ('belonging_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Column')),
            ],
        ),
        migrations.AddField(
            model_name='column',
            name='belonging_file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.File'),
        ),
    ]
