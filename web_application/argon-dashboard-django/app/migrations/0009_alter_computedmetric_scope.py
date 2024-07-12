# Generated by Django 4.2.14 on 2024-07-11 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_computedmetric_metrictype_delete_metrics_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='computedmetric',
            name='scope',
            field=models.CharField(choices=[('DATASET', 'Scope Dataset'), ('COLUMN', 'Scope Column')], default='DATASET', max_length=255),
        ),
    ]
