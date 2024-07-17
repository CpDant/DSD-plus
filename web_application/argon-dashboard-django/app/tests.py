# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
import sys
import django
from unipath import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from .models import File, Column, DetectedSmell, SmellType, Parameter, Group, MetricType, ComputedMetric
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
from django.urls import reverse 
from datetime import datetime
from .views import customize, upload, result, saved, file_smells
from .forms import ParameterForm
from django.middleware.csrf import get_token

BASE_DIR = Path(__file__).parent
LIBRARY_DIR = Path(__file__).parent.parent.parent.parent
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
settings_dir = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.dirname(settings_dir))
SMELL_FOLDER = os.path.join(PROJECT_ROOT, 'app/test_sets/')

cwd = os.getcwd()
sys.path.append(LIBRARY_DIR+"/data_smell_detection/")

from datasmelldetection.core.datasmells import DataSmellType

smells_columns = {"smells":[
                    "DataSmellType.EXTREME_VALUE_SMELL",
                    "DataSmellType.SUSPECT_SIGN_SMELL",
                    "DataSmellType.MISSING_VALUE_SMELL",
                    "DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL",
                    "DataSmellType.INTEGER_AS_STRING_SMELL"
                ], "columns":[
                    "Age",
                    "Name",
                    "PClass",
                    "Sex",
                    "SexCode",
                    "Survived"
                ]}
smells = {"smells":[
            "DataSmellType.EXTREME_VALUE_SMELL",
            "DataSmellType.SUSPECT_SIGN_SMELL",
            "DataSmellType.MISSING_VALUE_SMELL",
            "DataSmellType.FLOATING_POINT_NUMBER_AS_STRING_SMELL",
            "DataSmellType.INTEGER_AS_STRING_SMELL"
        ], "columns":[
        ]}
columns = {"smells":[], 
           "columns":[
            "Age",
            "Name",
            "PClass",
            "Sex",
            "SexCode",
            "Survived"
          ]}
empty = {"smells":[], 
         "columns":[]
        }

class ViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Testuser', password='test', first_name='Test', last_name='Test')
        self.client.login(username='Testuser', password='test')
        self.group1 = Group(group_name='Group test')
        self.group1.save()
        self.file1 = File(file_name='test_sets/test.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()

        self.column1 = Column(column_name='Age', belonging_file=self.file1)
        self.column1.save()
        self.column2 = Column(column_name='Name', belonging_file=self.file1)
        self.column2.save()

        self.smell_type1 = SmellType(smell_type='Missing Value Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)

        self.smell_type2 = SmellType(smell_type='Duplicated Value Smell')
        self.smell_type2.save()
        self.smell_type2.belonging_file.add(self.file1)

        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()

        self.parameter2 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type2, belonging_file=self.file1)
        self.parameter2.save()

        self.metric_type1 = MetricType(metric_type='Completeness')
        self.metric_type1.save()
        self.metric_type2 = MetricType(metric_type='Uniqueness')
        self.metric_type2.save()
        self.metric_type3 = MetricType(metric_type='Validity')
        self.metric_type3.save()

        self.computed_metric1 = ComputedMetric.objects.create(value= 90.35, metric_type=self.metric_type1, scope=ComputedMetric.Scope.DATASET, belonging_scope_dataset=self.file1)
        self.computed_metric2 = ComputedMetric.objects.create(value= 80.31, metric_type=self.metric_type2, scope=ComputedMetric.Scope.DATASET, belonging_scope_dataset=self.file1)
        self.computed_metric3 = ComputedMetric.objects.create(value= 60.25, metric_type=self.metric_type3, scope=ComputedMetric.Scope.DATASET, belonging_scope_dataset=self.file1)
        self.factory = RequestFactory()

    def test_upload_csv_file(self):
        with open(SMELL_FOLDER+'test.csv', 'rb') as csv_file:
            request = self.factory.post(reverse('upload'), {'upload': csv_file}, content_type='text/csv')
            request.user = self.user
            response = upload(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, 'index.html')

    def test_upload_png_file(self):
        with open(SMELL_FOLDER+'test.png') as csv_file:
            request = self.factory.post(reverse('upload'), {'upload': csv_file}, content_type='text/csv')
            request.user = self.user
            response = upload(request)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload a .csv file')

    def test_customize(self):
        request = self.factory.post(reverse('customize'))
        request.user = self.user
        response = customize(request)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.context_data['forms']['Believability Smells'][DataSmellType('Duplicated Value Smell')]['checkbox'], 'smell_checked')
        self.assertEqual(response.context_data['forms']['Believability Smells'][DataSmellType('Duplicated Value Smell')]['mostly'][0], self.parameter2)

        self.assertEqual(response.context_data['forms']['Syntactic Understandability Smells'][DataSmellType('Missing Value Smell')]['checkbox'], 'smell_checked')
        self.assertEqual(response.context_data['forms']['Syntactic Understandability Smells'][DataSmellType('Missing Value Smell')]['mostly'][0], self.parameter1)
        self.assertEqual(response.context_data['forms']['Encoding Understandability Smells'], {})
        self.assertEqual(response.context_data['forms']['Consistency Smells'], {})

        request1 = self.factory.post(reverse('customize'), smells)
        request1.user = self.user
        response = customize(request1)
        self.assertEqual(response.context_data['message'], 'Select smells AND columns.')

        request2 = self.factory.post(reverse('customize'), empty)
        request2.user = self.user
        response = customize(request2)
        self.assertEqual(response.context_data['message'], 'Select smells AND columns.')

        request3 = self.factory.post(reverse('customize'), columns)
        request3.user = self.user
        response = customize(request3)
        self.assertEqual(response.context_data['message'], 'Select smells AND columns.')

        self.assertEqual(response.template_name, 'customize.html')

    def test_result(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        response = result(request)
        self.assertEqual(response.context_data['column_names'], [self.column1.column_name, self.column2.column_name])
        self.assertEqual(response.context_data['file'], self.file1.file_name)

        request1 = self.factory.post(reverse('result'), {'del': [self.file1.file_name]})
        request1.user = self.user
        response = result(request1)
        self.assertEqual(response.context_data['delete_message'], 'Result deleted and not viewable in Saved Results.')
        self.assertEqual(response.template_name, 'results.html')

    def test_saved_results(self):
        self.detected_smell = DetectedSmell.objects.create(data_smell_type=self.smell_type1, total_element_count=200, faulty_element_count=10, faulty_list=["hi", "jo", "ho"], belonging_column=self.column1)
        request = self.factory.get('/')
        request.user = self.user
        csrf_token = get_token(request)
        post_data = {
            'csrfmiddlewaretoken': csrf_token,
            'filename': 'test.csv',
            'group-name': 'Group test'
        }
        request = self.factory.post(reverse('filesmells'), post_data)
        request.user = self.user
        response = file_smells(request)
        self.assertEqual(response.context_data['results'], {'test': {self.column1: [self.detected_smell], self.column2: []}})
        request1 = self.factory.post(reverse('filesmells'), {'del': [self.file1.file_name]})
        request1.user = self.user
        response = file_smells(request1)
        self.assertEqual(response.context_data['results'], {})

class ParameterFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Testuser', password='test', first_name='Test', last_name='Test')
        self.client.login(username='Testuser', password='test')
        self.group1 = Group(group_name='Group test')
        self.group1.save()
        self.file1 = File(file_name='Test.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.smell_type = SmellType(smell_type='Missing Value Smell')
        self.smell_type.save()
        self.smell_type.belonging_file.add(self.file1)

    def test_parameter_form_inside_interval(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=1.0, value=0.5, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertTrue(form.is_valid())

    def test_parameter_form_outside_interval(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=1.0, value=3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertFalse(form.is_valid())

    def test_parameter_form_inside_interval_max_inf(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=-1.0, value=3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertTrue(form.is_valid())

    def test_parameter_form_outside_interval_max_inf(self):
        self.parameter = Parameter.objects.create(name="mostly", min_value=0.0, max_value=-1.0, value=-3.0, belonging_smell=self.smell_type, belonging_file=self.file1)
        self.parameter.save()
        form = ParameterForm(data={'value': self.parameter.value}, instance=self.parameter)
        self.assertFalse(form.is_valid())

class ComputeMetricTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Testuser', password='test', first_name='Test', last_name='Test')
        self.client.login(username='Testuser', password='test')
        self.group1 = Group(group_name='Group test')
        self.group1.save()
        self.metric_type1 = MetricType(metric_type='Completeness')
        self.metric_type1.save()
        self.metric_type2 = MetricType(metric_type='Uniqueness')
        self.metric_type2.save()
        self.metric_type3 = MetricType(metric_type='Validity')
        self.metric_type3.save()
        self.factory = RequestFactory()
    def test_no_faulty_element(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_01_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        response = result(request)
        self.assertEqual(100.00, response.context_data['global_comp_test'])
        self.assertEqual(100.00, response.context_data['global_uniq_test'])
        self.assertEqual(100.00, response.context_data['global_val_test'])

    def test_completeness(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_02_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        self.smell_type1 = SmellType(smell_type='Missing Value Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)
        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()
        response = result(request)
        self.assertEqual(80.00, response.context_data['global_comp_test'])
        self.assertEqual(100.00, response.context_data['global_uniq_test'])
        self.assertEqual(100.00, response.context_data['global_val_test'])

    def test_uniqueness(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_03_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        self.smell_type1 = SmellType(smell_type='Duplicated Value Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)
        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()
        response = result(request)
        self.assertEqual(100.00, response.context_data['global_comp_test'])
        self.assertEqual(40.00, response.context_data['global_uniq_test'])
        self.assertEqual(100.00, response.context_data['global_val_test'])
    def test_validity_with_int_value_as_string(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_04_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        self.smell_type1 = SmellType(smell_type='Integer As String Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)
        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()
        response = result(request)
        self.assertEqual(100.00, response.context_data['global_comp_test'])
        self.assertEqual(100.00, response.context_data['global_uniq_test'])
        self.assertEqual(90.00, response.context_data['global_val_test'])

    def test_validity_with_int_value_as_float(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_05_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        self.smell_type1 = SmellType(smell_type='Integer As Floating Point Number Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)
        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()
        self.parameter2 = Parameter(name="epsilon", min_value=0.0, max_value="inf", value=1e-6, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter2.save()
        response = result(request)
        self.assertEqual(100.00, response.context_data['global_comp_test'])
        self.assertEqual(100.00, response.context_data['global_uniq_test'])
        self.assertEqual(0.00, response.context_data['global_val_test']) #Qui il problema è che pandas fa il cast
                                                                         #di tutte le componenti nel tipo float e
                                                                         #dunque sarà sempre questo il comportamento

    def test_validity_with_float_value_as_string(self):
        request = self.factory.get(reverse('result'))
        request.user = self.user
        self.file1 = File(file_name='input_TC_06_CR_02.csv', user=self.user, uploaded_time=datetime.now(), group_name= self.group1)
        self.file1.save()
        self.column1 = Column(column_name='column', belonging_file=self.file1)
        self.column1.save()
        self.smell_type1 = SmellType(smell_type='Floating Point Number As String Smell')
        self.smell_type1.save()
        self.smell_type1.belonging_file.add(self.file1)
        self.parameter1 = Parameter(name="mostly", min_value=0.0, max_value=1.0, value=1.0, belonging_smell=self.smell_type1, belonging_file=self.file1)
        self.parameter1.save()
        response = result(request)
        self.assertEqual(100.00, response.context_data['global_comp_test'])
        self.assertEqual(100.00, response.context_data['global_uniq_test'])
        self.assertEqual(50.00, response.context_data['global_val_test'])
    

