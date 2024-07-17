from app.models import MetricType, ComputedMetric, Column


def compute_metric(datasmells, all_columns, involved_smells, metric_name):
    metric_map = {}
    global_elements, global_faulty_elements = 0, 0
    detected_columns = []
    not_detected_columns = []

    total_rows, total_columns = 0, len(all_columns)

    # if there are datasmells you need to compute metrics
    if len(datasmells) > 0:

        # filter the names of the 'detected columns' (the ones that have at least one smell)
        for column in datasmells.items():
            detected_columns.append(column[0])

        # filter the names of the 'non-detected columns'
        for column in all_columns:
            if column not in detected_columns:
                not_detected_columns.append(column)

        # compute the rows number by the element of a column
        for column, column_smells in datasmells.items():
            for smell in column_smells:
                total_rows = smell.statistics.total_element_count
                break
            break

        # filter the 'detected column' for the involved smells needed in order to compute the metric
        for column, column_smells in datasmells.items():
            for smell in column_smells:
                if smell.data_smell_type.value in involved_smells:
                    metric = ((smell.statistics.total_element_count - smell.statistics.faulty_element_count) /
                              smell.statistics.total_element_count) * 100
                    metric_map[column] = round(metric, 2)
                    global_faulty_elements += smell.statistics.faulty_element_count
                else:
                    # if a column does not any instances of the involved smell, the metric is automatically at 100%
                    metric_map[column] = 100

        # if the column is a 'not-detected' one, it means the metric is automatically at 100%
        for column in not_detected_columns:
            metric_map[column] = 100

        global_elements = total_rows * total_columns
        global_metric = ((global_elements - global_faulty_elements) / global_elements) * 100
        metric_map[("GLOBAL_" + metric_name)] = round(global_metric, 2)
        return metric_map

    else:
        # if there aren't any 'detected columns', it means that all the columns are okay, metric is at 100%
        for column in all_columns:
            metric_map[column] = 100
        metric_map[("GLOBAL_" + metric_name)] = 100
        return metric_map



def save_metric(file1, metric_values, metric_name):
    metric = MetricType.objects.get(metric_type=metric_name)

    # Save global metric to database
    ComputedMetric.objects.create(value=metric_values[("GLOBAL_" + metric_name)],
                                  metric_type=metric,
                                  scope=ComputedMetric.Scope.DATASET,
                                  belonging_scope_dataset=file1)

    # Save column metric to database
    for k, v in metric_values.items():
        if k != ("GLOBAL_" + metric_name):
            ComputedMetric.objects.create(value=v,
                                          metric_type=metric,
                                          scope=ComputedMetric.Scope.COLUMN,
                                          belonging_scope_column=Column.objects.get(column_name=k,
                                                                                    belonging_file=file1))


def retrieve_metric(f, metric_name, all_columns):
    metric = {}

    global_metric = ComputedMetric.objects.get(belonging_scope_dataset=f,
                                               metric_type=MetricType.objects.get(metric_type=metric_name))

    metric[("GLOBAL_" + metric_name)] = str(global_metric.value)

    for c in all_columns:
        try:
            column_metric = ComputedMetric.objects.get(belonging_scope_column=c,
                                                       metric_type=MetricType.objects.get(metric_type=metric_name))
            metric[c.column_name] = str(column_metric.value)
        except ComputedMetric.DoesNotExist:
            column_metric = None

    return metric
