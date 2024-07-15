# Generated by Django 4.2.14 on 2024-07-11 14:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20240526_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completeness', models.DecimalField(decimal_places=2, max_digits=5)),
                ('validity', models.DecimalField(decimal_places=2, max_digits=5)),
                ('uniqueness', models.DecimalField(decimal_places=2, max_digits=5)),
                ('belonging_scope_column', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.column')),
                ('belonging_scope_dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.file')),
            ],
        ),
    ]