# Calculate global and single columns completeness
def compute_completeness(datasmells):
    completeness_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.statistics.total_element_count
            break
        break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if smell.data_smell_type.value == "Missing Value Smell":
                completeness = ((smell.statistics.total_element_count - smell.statistics.faulty_element_count) /
                                smell.statistics.total_element_count) * 100
                completeness_map[column] = round(completeness, 2)

                global_faulty_elements += smell.statistics.faulty_element_count

    global_elements = total_rows * total_columns
    global_completeness = ((global_elements - global_faulty_elements) / global_elements) * 100
    completeness_map["GLOBAL_COMPLETENESS"] = round(global_completeness, 2)
    return completeness_map


# Calculate global and single columns uniqueness
def compute_uniqueness(datasmells):
    uniqueness_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())
    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.statistics.total_element_count
            break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if smell.data_smell_type.value == "Duplicated Value Smell":
                uniqueness = ((smell.statistics.total_element_count - smell.statistics.faulty_element_count) /
                              smell.statistics.total_element_count) * 100
                uniqueness_map[column] = round(uniqueness, 2)
                global_faulty_elements += smell.statistics.faulty_element_count

    global_elements = total_rows * total_columns
    global_uniqueness = ((global_elements - global_faulty_elements) / global_elements) * 100
    uniqueness_map["GLOBAL_UNIQUENESS"] = round(global_uniqueness, 2)
    return uniqueness_map


# Calculate global and single columns validity
def compute_validity(datasmells):
    validity_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())
    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.statistics.total_element_count
            break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if (smell.data_smell_type.value == "Integer As String Smell" or
                    smell.data_smell_type.value == "Floating Point Number As String Smell" or
                    smell.data_smell_type.value == "Integer As Floating Point Number Smell"):
                validity = ((smell.statistics.total_element_count - smell.statistics.faulty_element_count) /
                            smell.statistics.total_element_count) * 100
                validity_map[column] = round(validity, 2)

                global_faulty_elements += smell.statistics.faulty_element_count

    global_elements = total_rows * total_columns
    global_validity = ((global_elements - global_faulty_elements) / global_elements) * 100
    validity_map["GLOBAL_VALIDITY"] = round(global_validity, 2)
    return validity_map
