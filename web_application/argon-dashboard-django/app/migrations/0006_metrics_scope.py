# Generated by Django 4.2.14 on 2024-07-11 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_metrics'),
    ]

    operations = [
        migrations.AddField(
            model_name='metrics',
            name='scope',
            field=models.CharField(default='Column', max_length=255),
        ),
    ]
