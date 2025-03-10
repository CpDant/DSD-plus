# Generated by Django 4.2.14 on 2024-07-11 16:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_metrics_scope'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metrics',
            name='belonging_scope_column',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.column'),
        ),
        migrations.AlterField(
            model_name='metrics',
            name='belonging_scope_dataset',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.file'),
        ),
    ]
