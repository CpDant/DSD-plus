# Calculate global and single columns completeness
def calculate_completeness(datasmells):
    completeness_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())
    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.total_element_count
            break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if smell.data_smell_type.smell_type == "Missing Value Smell":
                completeness = ((smell.total_element_count - smell.faulty_element_count) / smell.total_element_count) * 100
                completeness_map[column.column_name] = round(completeness, 2)

                global_faulty_elements += smell.faulty_element_count

    global_elements = total_rows * total_columns
    global_completeness = ((global_elements - global_faulty_elements) / global_elements) * 100
    completeness_map["GLOBAL_COMPLETENESS"] = round(global_completeness, 2)
    return completeness_map

# Calculate global and single columns uniqueness
def calculate_uniqueness(datasmells):
    uniqueness_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())
    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.total_element_count
            break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if smell.data_smell_type.smell_type == "Duplicated Value Smell":
                uniqueness = ((smell.total_element_count - smell.faulty_element_count) / smell.total_element_count) * 100
                uniqueness_map[column.column_name] = round(uniqueness, 2)

                global_faulty_elements += smell.faulty_element_count

    global_elements = total_rows * total_columns
    global_uniqueness = ((global_elements - global_faulty_elements) / global_elements) * 100
    uniqueness_map["GLOBAL_UNIQUENESS"] = round(global_uniqueness, 2)
    return uniqueness_map

# Calculate global and single columns validity
def calculate_validity(datasmells):
    validity_map = {}
    global_elements, global_faulty_elements = 0, 0

    total_rows, total_columns = 0, len(datasmells.keys())
    for column, column_smells in datasmells.items():
        for smell in column_smells:
            total_rows = smell.total_element_count
            break

    for column, column_smells in datasmells.items():
        for smell in column_smells:
            if smell.data_smell_type.smell_type == "Integer As String Smell" or smell.data_smell_type.smell_type == "Floating Point Number As String Smell" or smell.data_smell_type.smell_type == "Integer As Floating Point Number Smell":
                validity = ((smell.total_element_count - smell.faulty_element_count) / smell.total_element_count) * 100
                validity_map[column.column_name] = round(validity, 2)

                global_faulty_elements += smell.faulty_element_count

    global_elements = total_rows * total_columns
    global_validity = ((global_elements - global_faulty_elements) / global_elements) * 100
    validity_map["GLOBAL_VALIDITY"] = round(global_validity, 2)
    return validity_map