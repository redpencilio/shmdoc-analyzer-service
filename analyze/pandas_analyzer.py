# Import pandas
import pandas as pd
import math
import json
import datefinder
from pprint import pprint
from collections import Counter
from numpyencoder import NumpyEncoder
from datetime import datetime
from urllib.parse import urlparse

try:
    from .. import column as column_file  # Use this one when using docker
except:
    import column as column_file  # Use this one when using debug.py

from statistics import median

typeUri = "http://www.w3.org/2001/XMLSchema#{type}"
typeMap = {bool: typeUri.format(type="boolean"),
           int: typeUri.format(type="integer"),
           float: typeUri.format(type="float"),
           str: typeUri.format(type="string"),
           "datetime": typeUri.format(type="dateTime")
           "uri": typeUri.format(type="anyURI"}


def type_url(type):
    global typeMap
    return typeMap[type]


def is_datetime(string):
    # Check whether there's any date / datetime somewhere in the string
    matches = datefinder.find_dates(string)
    try:
        for match in matches:
            # I didn't find a way to check len(matches) or matches.empty, so this iteration solves it
            return True
    except TypeError:
        pass  # No idea why a TypeError is raised sometimes, but this solves the problem temporarily :-)
    return False


def is_uri(string):
    # Check wheter there's a uri in this string
    # NOTE: this function will only check for absolute URI's, relative URI's are not accepted.
    # Even though the xsd:type used is anyURI (which also encompasses relative URI's)
    # source https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    try:
        result = urlparse(string)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False
    


# Given a string, what does the string probably contain?
def analyze_string_type(element, occurrences):
    supported_strings = {"datetime": is_datetime,
                         "uri"     : is_uri}

    added_somewhere = False
    for type in supported_strings:
        # Check whether the string can be the current type
        if supported_strings[type](element):
            # Created the type in the dict if it doesn't occur yet
            if type_url(type) not in occurrences:
                occurrences[type_url(type)] = 0
            # Found an occurrence
            added_somewhere = True
            occurrences[type_url(type)] += 1

    if not added_somewhere:
        # Fit's none of the types, so it's just a string
        if type_url(str) not in occurrences:
            occurrences[type_url(str)] = 0
        occurrences[type_url(str)] += 1

    return occurrences


def analyze_string_row(column_data):
    # Finds the probable type for a row containing (mainly) strings
    occurrences = dict()
    for element in column_data:
        if not isinstance(element, str):
            continue
        occurrences = analyze_string_type(element, occurrences)
    probable_type = find_most_occuring(occurrences)
    # make_dict_relative(occurrences, column_data.size)
    return probable_type


def analyze_most_common(column_data):
    # GEt the top 5 most occuring elements in the column with their relative occurrence

    common_elements = []

    try:
        # Get inforation about the most occuring elements
        c = Counter(column_data)
        most_common_element = c.most_common(5)  # get the nr. 5 most occuring elements

        for el in most_common_element:
            occurrence = {"element": el[0], "occurrences": el[1] / column_data.size}
            common_elements.append(occurrence)
    except TypeError:
        # Typerror possible if data contains e.g. a list
        return []
    return common_elements


def make_dict_relative(dictionary, size):
    for type in dictionary:
        idx = type_url(type)
        if isinstance(dictionary[idx], dict):
            dictionary[idx] = make_dict_relative(dictionary[idx], size)
        else:
            dictionary[idx] = dictionary[idx] / size
    return dictionary


def find_most_occuring(occurrences):
    # Given a dict containing elements with a key and a number as value, get the key with the highest value
    global typeUri
    # No most occuring, so it can be any type
    most_occuring = typeUri.format(type="anyType")
    most_occuring_count = 0
    for type in occurrences:
        if type == "empty":
            # Skip empty fields (e.g. 3 empty, 1 str, then it should be a str instead of empty)
            continue
        if occurrences[type] > most_occuring_count:
            most_occuring_count = occurrences[type]
            most_occuring = type
    return most_occuring


def predict_type(column_data, col_obj):
    occurrences = dict()

    global typeMap
    # No occurrences at the beginning
    occurrences["empty"] = 0
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
            # Only check for trivial types (int, float, str, bool)
            # Other types (e.g. datetime) must be checked afterwards
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


def export_json(filename, data):
    # Ecport the 'data' dictionary as json
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True,
                  separators=(', ', ': '), ensure_ascii=False,
                  cls=NumpyEncoder)


def get_string_lengths(column_data):
    # Get a set containing the length of the elements in the database
    lengths = set()
    for el in column_data:
        try:
            if el is not None:
                lengths.add(len(el))
        except:
            continue
    return lengths


def analyze(data):
    """
    The main analyze function
    The parameter data is a pandas dataframe
    Returns a list of columns: for each column of the data an object with the information attached
    """
    # TODO: Null
    columns = []

    # finding the type of each column
    for column in data:
        # TODO: Check for changes sinces last analysis (if not changed, you can skip the analysis)
        #  Also check previously created col_obj whether we should process (col_obj.disable_processing)
        #  For this we should keep track of when the last analysis was

        print("Analyzing column {}".format(column))
        col_obj = column_file.Column(column)

        # Get the data from the current column
        column_data = data[column]

        # Arguments get passed by reference (and edited)
        predict_type(column_data, col_obj)

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

        str_types = [type_url(str), type_url("datetime")]
        if col_obj.data_type in str_types:
            str_lengths = get_string_lengths(column_data)
            col_obj.mean = 0 if len(str_lengths) == 0 else (
                    float(sum(str_lengths)) / len(str_lengths))  # the avg length
            col_obj.median = median(str_lengths)  # statistics.median
            col_obj.min = min(str_lengths)  # min length
            col_obj.max = max(str_lengths)  # max length

        columns.append(col_obj)

    return columns
