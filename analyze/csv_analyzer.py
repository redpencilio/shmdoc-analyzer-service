# Import pandas
import pandas as pd
import math
import json
import datefinder
from pprint import pprint
from collections import Counter
from numpyencoder import NumpyEncoder
from datetime import datetime
from .. import column as column_file # Use this one when using docker
# from column import Column # Use this one when using debug.py # TODO add if statement
from statistics import median

typeUri = "http://www.w3.org/2001/XMLSchema#{type}"
typeMap = {bool: typeUri.format(type="boolean"),
           int: typeUri.format(type="integer"),
           float: typeUri.format(type="float"),
           str: typeUri.format(type="string"),
           "datetime": typeUri.format(type="dateTime")}


def type_url(type):
    global typeMap
    return typeMap[type]


def is_datetime(string):
    # Check whether there's any date / datetime somewhere in the string
    # stricts requires there to be a year, month and day (without strict, even strings like "error" are a date somehow)
    matches = datefinder.find_dates(string)
    # TODO: find out why the for loop doesn't work on the docker and whether the if matches works
    try:
        for match in matches:
            # I didn't find a way to check len(matches), so this iteration solves it
            return True
    except TypeError:
        pass  # No idea why a TypeError is raised sometimes, but this solves the problem temporarily :-)
    return False


# Given a string, what does the string probably contain?
def analyze_string_type(element, occurrences):
    supported_strings = {"datetime": is_datetime}

    for type in supported_strings:
        if supported_strings[type](element):
            if type not in occurrences:
                occurrences[type_url(type)] = 0
            occurrences[type_url(type)] += 1
        else:
            if type_url(str) not in occurrences:
                occurrences[type_url(str)] = 0
            occurrences[type_url(str)] += 1

    return occurrences


def analyze_string_row(column_data):
    occurrences = dict()
    for element in column_data:
        if not isinstance(element, str):
            continue
        occurrences = analyze_string_type(element, occurrences)
    probable_type = find_most_occuring(occurrences)
    # make_dict_relative(occurrences, column_data.size)
    return probable_type


def analyze_most_common(column_data):
    common_elements = []

    try:
        # Get inforation about the most occuring elements
        c = Counter(column_data)
        most_common_element = c.most_common(5)  # get the nr. 5 most occuring elements

        for el in most_common_element:
            occurance = {"element": el[0], "occurances": el[1] / column_data.size}
            common_elements.append(occurance)
    except TypeError:
        # Typerror possible if data contains e.g. a list
        return []
    return common_elements


def predict_seperator(filename):
    file = open(filename, "r")
    first_row = file.readline()

    possible_seperators = [';', '\t', ',']
    current_seperator = ''
    occurances = 0

    for sep in possible_seperators:
        count = first_row.count(sep)
        if count > occurances:
            occurances = count
            current_seperator = sep

    return current_seperator


def make_dict_relative(dictionary, size):
    for type in dictionary:
        idx = index(type)
        if isinstance(dictionary[idx], dict):
            dictionary[idx] = make_dict_relative(dictionary[idx], size)
        else:
            dictionary[idx] = dictionary[idx] / size
    return dictionary


def find_most_occuring(occurrences):
    most_occuring = "I have no idea :-("
    most_occuring_count = 0
    for type in occurrences:
        if occurrences[type] > most_occuring_count:
            most_occuring_count = occurrences[type]
            most_occuring = type
    return most_occuring


def predict_type(column_data, col_obj):
    occurrences = dict()
    occurrences["empty"] = 0

    global typeMap
    # No occurrences at the beginning
    for type_ in typeMap:
        occurrences[type_url(type_)] = 0

    # Find the absolute occurances of each type
    for element in column_data:
        # float check because math.isnan() only works on real numbers
        if isinstance(element, float) and math.isnan(element):
            # Empty cells get converted to NaN by pandas
            occurrences["empty"] += 1
            occurrences[type_url(float)] -= 1  # Because it's actually not a float, but empty

        for type_ in typeMap:
            if isinstance(type_, type):
                if isinstance(element, type_):
                    occurrences[type_url(type_)] += 1

    col_obj.missing_count = occurrences["empty"]

    # Get the most occurring type
    expected_type = find_most_occuring(occurrences)

    if expected_type == type_url(str):
        # Analyze what type the string actualy is
        expected_type = analyze_string_row(column_data)

    if expected_type != "empty":
        col_obj.data_type = expected_type
    else:
        # Don't process columns with only empty elements
        col_obj.disable_processing = True

    # Make the absolute values relative
    # TODO: still relative required?
    # occurrences = make_dict_relative(occurrences, column_data.size)

    return col_obj


def export_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True,
                  separators=(', ', ': '), ensure_ascii=False,
                  cls=NumpyEncoder)
    # with open(filename, 'w') as fp:
    #     json.dump(data, fp)


def analyze(data):
    """
    The main analyze function
    The parameter data is a pandas dataframe
    Returns a list of columns: for each column of the data an object with the information attached
    """
    columns = []

    data_info = dict()  # Contains the info about each column

    # finding the type of each column
    for column in data:
        col_obj = column_file.Column(column)  # TODO: Retrieve previously created col_obj and check if we should process

        column_data = data[column]
        stats = dict()

        col_obj = predict_type(column_data, col_obj)
        if col_obj.disable_processing:
            # Can be enabled if all empty
            # There is nothing useful to say about most common nan's in an empty column
            continue

        col_obj.record_count = column_data.size
        col_obj.common_values = analyze_most_common(column_data)

        numerical_types = [type_url(bool), type_url(int), type_url(float)]
        if col_obj.data_type in numerical_types:
            col_obj.mean = column_data.mean()
            col_obj.median = column_data.median()
            col_obj.min = column_data.min()
            col_obj.max = column_data.max()
            stats["sd"] = column_data.std()  # Standard deviation

        str_types = [type_url(str), type_url("datetime")]
        if col_obj.data_type in str_types:
            str_lengths = [len(el) for el in column_data]
            col_obj.mean = 0 if len(str_lengths) == 0 else (
                        float(sum(str_lengths)) / len(str_lengths))  # the avg length
            col_obj.median = median(str_lengths)  # statistics.median
            col_obj.min = min(str_lengths)  # min length
            col_obj.max = max(str_lengths)  # max length
            # stats["str-data"] = analyze_string_row(column_data) # gets already analyzed in type prediction

        # Add a timestamp for when the last update was
        stats["timestamp"] = str(datetime.now())

        data_info[column] = stats

        columns.append(col_obj)

    # pprint(data_info)
    export_json("report.json", data_info)

    return columns
    # return data_info
