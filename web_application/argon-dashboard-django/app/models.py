from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    group_name = models.CharField(max_length=100, primary_key=True)

class File(models.Model):
    file_name = models.CharField(max_length=255, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_time = models.DateTimeField(auto_now_add=True,)
    group_name = models.ForeignKey(Group, on_delete=models.CASCADE)

class SmellType(models.Model):
    smell_type = models.CharField(max_length=255, primary_key=True)
    belonging_file = models.ManyToManyField(File)

class Column(models.Model):
    column_name = models.CharField(max_length=100)
    belonging_file = models.ForeignKey(File, on_delete=models.CASCADE)

class DetectedSmell(models.Model):
    data_smell_type = models.ForeignKey(SmellType, on_delete=models.CASCADE)    
    total_element_count = models.IntegerField()
    faulty_element_count = models.IntegerField()
    faulty_list = models.CharField(max_length=1024)
    belonging_column = models.ForeignKey(Column, on_delete=models.CASCADE)

class Parameter(models.Model):
    name = models.CharField(max_length=255)
    min_value = models.FloatField()
    max_value = models.FloatField()
    value = models.FloatField(blank=True, null=True)
    belonging_smell = models.ForeignKey(SmellType, on_delete=models.CASCADE)
    belonging_file = models.ForeignKey(File, on_delete=models.CASCADE)

class MetricType(models.Model):
    metric_type = models.CharField(max_length=255, primary_key=True)

class ComputedMetric(models.Model):
    class Scope(models.TextChoices):
        DATASET = 'DATASET', 'Scope Dataset'
        COLUMN = 'COLUMN', 'Scope Column'

    value = models.DecimalField(max_digits=5, decimal_places=2)
    metric_type = models.ForeignKey(MetricType, on_delete=models.CASCADE)
    scope = models.CharField(max_length=255, choices=Scope.choices, default=Scope.DATASET)
    belonging_scope_dataset = models.ForeignKey(File, on_delete=models.CASCADE, null=True, blank=True)
    belonging_scope_column = models.ForeignKey(Column, on_delete=models.CASCADE, null=True, blank=True)
