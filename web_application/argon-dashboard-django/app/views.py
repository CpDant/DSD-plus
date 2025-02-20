import pandas as pd
from django.template.defaulttags import register
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse
from django import template
from django.template.response import TemplateResponse
from django.core.files.storage import FileSystemStorage
from pandas.errors import EmptyDataError

from .forms import ParameterForm
import os
import sys
from app.models import File, Column, DetectedSmell, SmellType, Parameter, Group, MetricType
from app.manage_metrics import save_metric, compute_metric, retrieve_metric
from core.settings import SMELL_FOLDER, LIBRARY_DIR
import json
cwd = os.getcwd()
sys.path.append(LIBRARY_DIR + "/data_smell_detection/")
from datasmelldetection.detectors.great_expectations.dataset import FileBasedDatasetManager
from datasmelldetection.detectors.great_expectations.context import GreatExpectationsContextBuilder
from datasmelldetection.detectors.great_expectations.detector import DetectorBuilder
from datasmelldetection.detectors.great_expectations.detector import GreatExpectationsDetector
from datasmelldetection.detectors.great_expectations.profiler import DataSmellAwareProfiler
from datasmelldetection.detectors.great_expectations.detector import DataSmellAwareConfiguration
from datasmelldetection.core.detector import DetectionStatistics, DetectionResult
from datasmelldetection.core.datasmells import DataSmellType
from datasmelldetection.detectors.great_expectations.expectations import \
    ExpectColumnValuesToNotContainSpacingSmell, ExpectColumnValuesToNotContainSpecialCharacterSmell
from django.contrib import messages

# Different smells by its category
with open(SMELL_FOLDER + 'json/smells.json') as json_file:
    data = json.load(json_file)

with open(SMELL_FOLDER + 'json/presettings.json') as json_file:
    presettings_smells = json.load(json_file)

with open(SMELL_FOLDER + 'json/doc.json') as json_file:
    doc_file = json.load(json_file)

all_smells = {i: {DataSmellType(a): b for a, b in j.items()} for i, j in data.items()}
believability_smells = all_smells['Believability Smells']
syntactic_understandability_smells = all_smells['Encoding Understandability Smells']
encoding_understandability_smells = all_smells['Syntactic Understandability Smells']
consistency_smells = all_smells['Consistency Smells']


def index(request):
    context = {}
    context['segment'] = 'index'

    html_template = loader.get_template('index.html')
    return HttpResponse(html_template.render(context, request))

def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        context['segment'] = load_template
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))
    except:
        html_template = loader.get_template('page-403.html')
        return HttpResponse(html_template.render(context, request))


@login_required
def upload(request):
    global all_smells, believability_smells, syntactic_understandability_smells, encoding_understandability_smells, \
        consistency_smells

    # Some presettings for data smell detection
    outer = os.path.join(os.getcwd(), "../")
    context_builder = GreatExpectationsContextBuilder(
        os.path.join(outer, "../great_expectations"),
        os.path.join(cwd, "core/media")
    )
    con = context_builder.build()
    manager = FileBasedDatasetManager(context=con)
    context = {}

    # File upload
    if request.method == 'POST' and 'upload' in request.FILES:
        uploaded_file = request.FILES['upload']

        group_name = request.POST['input-group-name']

        if '.csv' in uploaded_file.name:
            df = None

            try:
                df = pd.read_csv(uploaded_file)
                df.dropna(how='all', axis=1, inplace=True)
                empty = df.empty
            except EmptyDataError:
                empty = True

            if not empty:
                fs = FileSystemStorage()
                file_name = fs.save(uploaded_file.name, uploaded_file)

                group = Group(group_name=group_name)
                group.save()

                # Save file to database
                file1 = File(file_name=file_name, user=request.user, group_name_id=group_name)
                file1.save()

                dataset = manager.get_dataset(file_name)

                context['url'] = fs.url(file_name)
                context['size'] = fs.size(file_name) / 1000000

                detector = DetectorBuilder(context=con, dataset=dataset).build()

                register_new_smells(detector)

                supported_smells = detector.get_supported_data_smell_types()

                # Save supported smell to database
                for s in supported_smells:
                    smell = SmellType(smell_type=s.value)
                    smell.save()
                    smell.belonging_file.add(file1)

                    # Save parameters for smells
                    parameters = believability_smells.get(s) or syntactic_understandability_smells.get(
                        s) or encoding_understandability_smells.get(s) or consistency_smells.get(s)
                    if parameters is not None:
                        for p, v in parameters.items():
                            if v["max"] != "inf":
                                par = Parameter(name=p, value=presettings_smells["tolerant"][s.value][p],
                                                belonging_smell=smell, belonging_file=file1, min_value=v["min"],
                                                max_value=v["max"])
                            else:
                                par = Parameter(name=p, value=presettings_smells["tolerant"][s.value][p],
                                                belonging_smell=smell, belonging_file=file1, min_value=v["min"],
                                                max_value=-1)
                            par.save()

                # Save columns to database
                columns = precheck_columns(dataset.get_column_names())
                for c in columns:
                    Column.objects.create(column_name=c, belonging_file=file1)

                # Save implemented metrics to database
                MetricType(metric_type="Completeness").save()
                MetricType(metric_type="Uniqueness").save()
                MetricType(metric_type="Validity").save()
            else:
                context['message'] = 'Upload a non empty .csv file.'
                del df

        else:
            # Message if unsupported datatype was uploaded
            context['message'] = 'Upload a .csv file.'

    return TemplateResponse(request, 'index.html', context)


@login_required
def customize(request):
    global all_smells, believability_smells, syntactic_understandability_smells, encoding_understandability_smells, \
        consistency_smells
    context = {}

    # Get latest file and available smells of current user
    file1 = File.objects.filter(user_id=request.user.id).latest("uploaded_time")
    smells = SmellType.objects.all().filter(belonging_file=file1)

    # Get smells for certain file from all smells in order to keep subcategories
    smell_types = [s.smell_type for s in list(smells)]
    available_smells = {i: {a: b for (a, b) in j.items() if a.value in smell_types} for i, j in all_smells.items()}

    # Get column names by id and by name for user selection
    column_names_by_id = list(Column.objects.all().filter(belonging_file=file1))
    column_names = [c.column_name for c in column_names_by_id]

    # Smells and column names for customization
    context['smells'] = available_smells
    context['column_names'] = column_names
    data = {}
    forms = dict(available_smells)

    # After customization button submit
    if request.method == 'POST' and 'tolerant' not in request.POST and 'medium' not in request.POST and 'strict' not in request.POST:
        # Selected smells and column names
        smells_list = request.POST.getlist('smells')
        columns = request.POST.getlist('columns')

        # Set checkbox status
        checked_columns = {}
        for c in column_names:
            checked_columns[c] = "column_checked" if not columns or c in columns else "column_unchecked"

        context['column_names'] = dict(checked_columns)

        # Build smell dictionary with parameters for template
        forms = dict(available_smells)
        form_error = False

        # Get parameter values for every smell
        for k, values in available_smells.items():
            temp = dict(values)
            for v in values:
                smell_db = SmellType.objects.get(smell_type=v.value)
                parameter_list = list(Parameter.objects.all().filter(belonging_smell=smell_db, belonging_file=file1))

                # Set smell status
                form_dict = {}
                form_dict["checkbox"] = "smell_checked" if not smells_list or str(
                    v) in smells_list else "smell_unchecked"

                for p in parameter_list:
                    # Build prefix for form
                    prefix_name = str(v) + str(p)

                    form_dict[p.name] = list()
                    form_dict[p.name].append(p)
                    if len(request.POST) > 4:
                        form_dict[p.name].append(ParameterForm(request.POST, prefix=prefix_name, instance=p))

                        # Save values if form is valid or set error to True
                        if form_dict[p.name][1].is_valid():
                            form_dict[p.name][1].save()
                        elif "This field is required." not in form_dict[p.name][1].errors.as_json():
                            form_error = True

                    else:
                        form_dict[p.name].append(ParameterForm(prefix=prefix_name, instance=p))

                temp[v] = dict(form_dict)
            forms[k] = dict(temp)

        # If smells and columns had been selected and no error occurred
        if not form_error and smells_list and columns:
            context['list_smells'] = [s.split('.')[1].replace("_", " ") for s in smells_list]
            context['list_columns'] = columns

            # Delete columns and smells which should not be detected according to user's customization
            columns_to_delete = []
            for c in column_names_by_id:
                if c.column_name not in columns:
                    columns_to_delete.append(c.id)
            for c in columns_to_delete:
                Column.objects.get(id=c).delete()

            smells_to_delete = []
            for s in list(smells):
                if 'DataSmellType.' + s.smell_type.replace(" ", "_").upper() not in smells_list:
                    s.belonging_file.remove(file1)

        elif form_error:
            context['message'] = 'Invalid parameter values.'

        else:
            context['message'] = 'Select smells AND columns.'

            # Before customization button submit and/or presetting was selected
    else:
        # Build smell dictionary with parameters for template

        if 'tolerant' in request.POST:
            context['presetting'] = 'tolerant'

        elif 'medium' in request.POST:
            context['presetting'] = 'medium'

        elif 'strict' in request.POST:
            context['presetting'] = 'strict'
        else:
            context['presetting'] = None

        columns = request.POST.getlist('columns')

        # Set column status
        checked_columns = {}
        for c in column_names:
            checked_columns[c] = "column_checked" if not columns or c in columns else "column_unchecked"

        context['column_names'] = dict(checked_columns)
        for k, values in available_smells.items():
            temp = dict(values)

            for v in values:
                smell_db = SmellType.objects.get(smell_type=v.value)
                parameter_list = list(Parameter.objects.all().filter(belonging_smell=smell_db, belonging_file=file1))

                # Set smell status
                form_dict = {}
                form_dict["checkbox"] = "smell_checked" if not request.POST.getlist('smells') or str(
                    v) in request.POST.getlist('smells') else "smell_unchecked"

                for p in parameter_list:
                    prefix_name = str(v) + str(p)
                    form_dict[p.name] = list()
                    form_dict[p.name].append(p)

                    if context['presetting'] and p.name in presettings_smells[context['presetting']][v.value]:
                        data = {'value': presettings_smells[context['presetting']][v.value][p.name]}
                    else:
                        data = {'value': 1.0}

                    if context['presetting']:
                        form_dict[p.name].append(ParameterForm(initial=data, prefix=prefix_name, instance=p))
                    else:
                        form_dict[p.name].append(ParameterForm(prefix=prefix_name, instance=p))

                    form_dict[p.name].append("False")

                temp[v] = dict(form_dict)
            forms[k] = dict(temp)

    context['forms'] = forms
    context['forms_easy'] = forms
    context['doc'] = doc_file

    return TemplateResponse(request, 'customize.html', context)


@login_required
def result(request):
    # Some presettings for data smell detection
    context = {}
    completeness_values, uniqueness_values, validity_values = {}, {}, {}
    outer = os.path.join(os.getcwd(), "../")
    context_builder = GreatExpectationsContextBuilder(
        os.path.join(outer, "../great_expectations"),
        os.path.join(cwd, "core/media")
    )
    con = context_builder.build()
    manager = FileBasedDatasetManager(context=con)

    # Get file for detection
    try:
        file1 = File.objects.filter(user_id=request.user.id).latest("uploaded_time")

        # Delete file and detection result if button submit
        if request.method == 'POST':
            delete_file(file1.file_name)
            context['delete_message'] = 'Result deleted and not viewable in Saved Results.'
            return TemplateResponse(request, 'results.html', context)

        dataset = manager.get_dataset(file1.file_name)
        column_names = [c.column_name for c in list(Column.objects.all().filter(belonging_file=file1))]
        smells = list(SmellType.objects.all().filter(belonging_file=file1))

        # Build dict for data smell configuration
        ds_config = {}
        for s in smells:
            pars = list(Parameter.objects.all().filter(belonging_smell=s))
            par_dict = {}
            for p in pars:
                par_dict[p.name] = p.value

            temp = DataSmellType(s.smell_type)
            ds_config[temp] = dict(par_dict)

        conf = DataSmellAwareConfiguration(
            column_names=column_names,
            data_smell_configuration=ds_config
        )
        detector = DetectorBuilder(context=con, dataset=dataset).set_configuration(conf).build()

        # register the new implemented smells
        register_new_smells(detector)

        # Detect smells and sort result
        detected_smells = detector.detect()
        sorted_results = {}
        for c in column_names:
            if c in [i.column_name for i in detected_smells]:
                sorted_results[c] = []
                for s in detected_smells:
                    if s.column_name == c:
                        sorted_results[c].append(s)

        context['column_names'] = column_names
        context['results'] = sorted_results
        context['file'] = file1.file_name

        # compute metrics for the dataset and columns
        completeness_values = compute_metric(sorted_results, column_names, ["Missing Value Smell"], "Completeness")
        uniqueness_values = compute_metric(sorted_results, column_names, ["Duplicated Value Smell"], "Uniqueness")
        validity_values = compute_metric(sorted_results, column_names, ["Integer As String Smell",
                                                                        "Floating Point Number As String Smell",
                                                                        "Integer As Floating Point Number Smell"],
                                         "Validity")

        # Save detected smell to database
        for key, value in sorted_results.items():
            column1 = Column.objects.get(column_name=key, belonging_file=file1)
            for v in value:
                data_smell_t = SmellType.objects.get(smell_type=v.data_smell_type.value)
                DetectedSmell.objects.create(data_smell_type=data_smell_t,
                                             total_element_count=v.statistics.total_element_count,
                                             faulty_element_count=v.statistics.faulty_element_count,
                                             faulty_list=v.faulty_elements, belonging_column=column1)

        # Save dataset metrics to database
        save_metric(file1, completeness_values, "Completeness")
        save_metric(file1, uniqueness_values, "Uniqueness")
        save_metric(file1, validity_values, "Validity")

        context['global_comp_test'] = completeness_values['GLOBAL_Completeness']
        context['global_uniq_test'] = uniqueness_values['GLOBAL_Uniqueness']
        context['global_val_test'] = validity_values['GLOBAL_Validity']

    except Exception as e:
        print(e)
        context['no_result'] = 'No detection result for this user available.'

    return TemplateResponse(request, 'results.html', context)


# Saved view is only available for logged in users
@login_required
def saved(request):
    if request.method == 'POST':
        file_name = request.POST.get('del')
        try:
            File.objects.get(file_name=file_name).delete()
        except:
            pass

    # Some presettings for data smell detection
    context = {}
    groups = Group.objects.all()

    context['groups'] = list(groups)
    return TemplateResponse(request, 'saved-results.html', context)


# Datasmells info is only available for logged in users
@login_required
def file_smells(request):
    group_name = request.POST.get("group-name")
    context = {}

    # Retrieve all files by user and upload time
    files = File.objects.all().filter(user_id=request.user.id, group_name_id=group_name).order_by('uploaded_time')

    # Create dict for parameters
    parameter_dict = {}
    results = {}
    completeness_values, uniqueness_values, validity_values = {}, {}, {}
    for f in files:
        filename = f.file_name[:-4]
        all_columns = list(Column.objects.all().filter(belonging_file=f))
        all_smells_for_file = []
        for c in all_columns:
            all_smells_for_file.extend(list(DetectedSmell.objects.all().filter(belonging_column=c)))

        sorted_results = {}

        # Create dict for overall results
        smell_dict = {}
        for c in all_columns:
            sorted_results[c] = []
            for s in all_smells_for_file:
                if s.belonging_column.column_name == c.column_name:
                    sorted_results[c].append(s)
                    s_type = SmellType.objects.get(smell_type=s.data_smell_type.smell_type)
                    smell_dict[s.data_smell_type.smell_type] = list(
                        Parameter.objects.all().filter(belonging_smell=s_type, belonging_file=f))
                    parameter_dict[f.file_name[:-4]] = dict(smell_dict)

        context['parameter_dict'] = parameter_dict
        results[filename] = sorted_results

        completeness_values[f.file_name[:-4]] = retrieve_metric(f, "Completeness", all_columns)
        uniqueness_values[f.file_name[:-4]] = retrieve_metric(f, "Uniqueness", all_columns)
        validity_values[f.file_name[:-4]] = retrieve_metric(f, "Validity", all_columns)

    context['results'] = results
    context['group_name'] = group_name
    context['completeness_values'] = completeness_values
    context['uniqueness_values'] = uniqueness_values
    context['validity_values'] = validity_values

    global_comp, global_uniq, global_val = {}, {}, {}
    for key, value in completeness_values.items():
        global_comp[key] = value["GLOBAL_Completeness"]

    for key, value in uniqueness_values.items():
        global_uniq[key] = value["GLOBAL_Uniqueness"]

    for key, value in validity_values.items():
        global_val[key] = value["GLOBAL_Validity"]

    context["global_comp"] = global_comp
    context["global_uniq"] = global_uniq
    context["global_val"] = global_val

    return TemplateResponse(request, 'file-smells.html', context)


def register_new_smells(detector):
    # To add new expectations to the default registry, you need to create an instance of every expectation
    spacing = ExpectColumnValuesToNotContainSpacingSmell()
    special = ExpectColumnValuesToNotContainSpecialCharacterSmell()

    # Then you can register it into the registry of the detector
    spacing.register_data_smell(detector.registry)
    special.register_data_smell(detector.registry)


def retrieve_groups(request):
    groups = Group.objects.all()
    return_list = [g.group_name for g in groups]
    return JsonResponse({'list': return_list}, status=200, content_type="application/json")


# Remove row indexes
def precheck_columns(columns):
    if "Unnamed: 0" in columns:
        columns.remove("Unnamed: 0")
    return sorted(columns)


def delete_file(filename):
    file_to_delete = File.objects.get(file_name=filename)
    group_name = file_to_delete.group_name_id
    file_to_delete.delete()
    FileSystemStorage().delete(filename)
    files_belonging_group = File.objects.filter(group_name=group_name)
    print(files_belonging_group.count())
    if files_belonging_group.count() == 0:
        Group.objects.get(group_name=group_name).delete()


def delete_results(request):
    filename = request.POST.get('del') + ".csv"

    delete_file(filename)

    return redirect('saved')


# Get item of dictionary in template
@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
