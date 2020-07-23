# Import pandas
import pandas as pd
import math
import json
from pprint import pprint
from collections import Counter
from numpyencoder import NumpyEncoder
from datetime import datetime
from .type_checkers import *

try:
    from .. import column as column_file  # Use this one when using docker
except (ImportError, ValueError):
    import column as column_file  # Use this one when using debug.py

from statistics import median


class Type:
    # Name is just a name for reference within the code
    # Uri is the type uri (for linked data dinges)
    # Check_function is a function that accepts an element as parameter and returns true iff the element is of the type
    # Subtypes are possible types it can be, when the initial type has been chosen
    #   (e.g. when string is chosen, it can be datetime or url (or just a string))
    def __init__(self, name, uri, check_function, subtypes):
        self.name = name
        self.uri = uri
        self.validate = check_function
        self.subtypes = subtypes


typeUri = "http://www.w3.org/2001/XMLSchema#{type}"
# Order is important in typeMap: When both have the same nr of occurrences, the first one will get selected
boolean = Type("bool", typeUri.format(type="boolean"), is_bool, [])
integer = Type("int", typeUri.format(type="integer"), is_int, [])
float_num = Type("float", typeUri.format(type="float"), is_float, [])

string = Type("str", typeUri.format(type="string"), is_str, [])
string.subtypes.append(Type("datetime", typeUri.format(type="dateTime"), is_datetime, []))
string.subtypes.append(Type("uri", typeUri.format(type="anyURI"), is_uri, []))

anytype = Type("anyType", typeUri.format(type="anyType"), is_any, [])
# anyType is just the default, should never be selected with the validation tests (only as default if no occurrences)

supported_types = [boolean, integer, float_num, string, anytype]


def find_type(type_list, type):

    # Given a type, e.g. "bool", find it in the typelist
    for type_ in type_list:
        # Check the elements in the list
        if type == type_.name:
            return type_
        # Recursively check their subtypes
        if type_.subtypes: # check if not empty
            search_result = find_type(type_.subtypes, type)
            if search_result:
                return search_result
    return None


def type_url(type):
    global supported_types
    return find_type(supported_types, type).uri


def analyze_subtype(element, occurrences, expected_type_obj):
# Given an element, which of the expected_type_obj subtypes is it probably? Or is it just the expected_type_obj?

    added_somewhere = False
    for type in expected_type_obj.subtypes:
        # Check whether the string can be the current type
        if type.validate(element):
            # Created the type in the dict if it doesn't occur yet
            if type.name not in occurrences:
                occurrences[type.name] = 0
            # Found an occurrence
            added_somewhere = True
            occurrences[type.name] += 1

    if not added_somewhere:
        # Fit's none of the types, so it's just the base type
        if expected_type_obj.name not in occurrences:
            occurrences[expected_type_obj.name] = 0
        occurrences[expected_type_obj.name] += 1


def analyze_subtype_column(column_data, expected_type_obj):
    global supported_types

    # Finds the probable type for a row containing (mainly) elements of type expected_type_obj
    occurrences = dict()
    for element in column_data:
        if not expected_type_obj.validate(element):
            continue
        analyze_subtype(element, occurrences, expected_type_obj) # Add possible types for element to occurences
    # Get the most occuring of the analyzed types
    probable_type = find_most_occuring(occurrences)
    probable_type_obj = find_type(supported_types, probable_type)

    # If there are still subtypes left, recursively search for the most probably type in there
    if probable_type_obj.subtypes and probable_type_obj.name != expected_type_obj.name:
        probable_type = analyze_subtype_column(column_data, probable_type_obj)
        # probable_type_obj = find_type(supported_types, probable_type)


    return probable_type


def analyze_most_common(column_data):
    # GEt the top 5 most occuring elements in the column with their relative occurrence

    common_elements = []

    try:
        # Get inforation about the most occuring elements
        c = Counter(column_data)
        most_common_element = c.most_common(15)  # get the nr. 15 most occuring elements, select the top 5 that aren't NaN

        for el in most_common_element:
            if isinstance(el[0], float) and math.isnan(el[0]):
                # NaN's are not supported in json
                continue
            elif len(common_elements) == 5:
                break
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
    most_occuring = "anyType"
    most_occuring_count = 0
    for type in occurrences:
        if type == "empty" or type == "none":
            # Skip empty fields (e.g. 3 empty, 1 str, then it should be a str instead of empty)
            continue
        if occurrences[type] > most_occuring_count:
            most_occuring_count = occurrences[type]
            most_occuring = type
    return most_occuring


def predict_type(column_data, col_obj):
    occurrences = dict()

    global supported_types
    # No occurrences at the beginning
    occurrences["empty"] = 0
    occurrences["none"] = 0
    for type_ in supported_types:
        occurrences[type_.name] = 0

    # Find the absolute occurances of each type
    for element in column_data:
        # float check because math.isnan() only works on real numbers
        if isinstance(element, float) and math.isnan(element):
            # Empty cells get converted to NaN by pandas
            occurrences["empty"] += 1
            occurrences["float"] -= 1  # Because it's actually not a float, but empty

        if element is None:
            occurrences["none"] += 1

        for type_ in supported_types:
            # Only check for trivial types (int, float, str, bool)
            # Other types (e.g. datetime) must be checked afterwards
            if type_.validate(element):
                occurrences[type_.name] += 1

    col_obj.missing_count = occurrences["empty"]
    col_obj.null_count = occurrences["none"]

    if col_obj.missing_count == col_obj.record_count:
        # Don't process columns with only empty elements
        col_obj.disable_processing = True
        return

    # Get the most occurring type
    expected_type = find_most_occuring(occurrences)
    expected_type_obj = find_type(supported_types, expected_type)
    if expected_type_obj.subtypes: # Check if not empty
        # Analyze what subtype the type actualy is
        expected_type = analyze_subtype_column(column_data, expected_type_obj)

    if expected_type != "empty" and expected_type != "none":
        col_obj.data_type = type_url(expected_type)
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

def get_numerical_data(column_data):
    # Get a set containing the length of the elements in the database
    data = list()
    for el in column_data:
        try:
            if el is not None and not (isinstance(el, float) and math.isnan(el)):
                data.append(float(el))
        except:
            if is_bool(el):
                data.append(float(el in ['true', '1', 't', 'y', 'yes',]))
            continue
    return data

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
        col_obj.record_count = column_data.size

        # Arguments get passed by reference (and edited)
        predict_type(column_data, col_obj)

        if col_obj.disable_processing:
            # Can be enabled if all empty
            # There is nothing useful to say about most common nan's in an empty column
            columns.append(col_obj)
            continue

        col_obj.common_values = analyze_most_common(column_data)

        num_analysis = False
        numerical_types = [type_url("bool"), type_url("int"), type_url("float")]
        if col_obj.data_type in numerical_types:
            numerical_data = get_numerical_data(column_data)
            num_analysis = True

        str_types = [type_url("str"), type_url("datetime")]
        if col_obj.data_type in str_types:
            num_analysis = True
            numerical_data = get_string_lengths(column_data)

        if num_analysis:
            col_obj.mean = 0 if len(numerical_data) == 0 else (
                    float(sum(numerical_data)) / len(numerical_data))  # the avg length
            col_obj.median = median(numerical_data)  # statistics.median
            col_obj.min = min(numerical_data)  # min length
            col_obj.max = max(numerical_data)  # max length

        columns.append(col_obj)

    return columns
