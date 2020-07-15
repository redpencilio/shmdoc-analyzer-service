# Import pandas
import pandas as pd
import math
import json
import datefinder
from pprint import pprint
from collections import Counter
from numpyencoder import NumpyEncoder
from datetime import datetime
from .column import Column
from statistics import median


def get_types():
    return {bool: "bool", int: "int", float: "float", str: "str"}


# Todo: occurances should not be global
def index(element):
    types = get_types()
    return types[element] if isinstance(element, type) else element


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
                occurrences[type] = 0
            occurrences[type] += 1

    return occurrences


def analyze_string_row(column_data):
    occurrences = dict()
    for element in column_data:
        occurrences = analyze_string_type(element, occurrences)
    make_dict_relative(occurrences, column_data.size)
    return occurrences


def analyze_most_common(column_data):
    common_elements = []

    # Get inforation about the most occuring elements
    c = Counter(column_data)
    most_common_element = c.most_common(5)  # get the nr. 5 most occuring elements

    for el in most_common_element:
        occurance = {"element": el[0], "occurances": el[1] / column_data.size}
        common_elements.append(occurance)

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


def count_type_occurances(column_data, col_obj):
    occurrences = dict()
    occurrences["empty"] = 0

    types = get_types()
    for type in types:
        occurrences[index(type)] = 0

    for element in column_data:
        # float check because math.isnan() only works on real numbers
        if isinstance(element, float) and math.isnan(element):
            # Empty cells get converted to NaN by pandas
            occurrences["empty"] += 1
            occurrences[index("float")] -= 1  # Because it's actually not a float, but empty

        for type in types:
            if isinstance(element, type):
                occurrences[index(type)] += 1

    col_obj.missing_count = occurrences["empty"]

    expected_type = "?"
    expected_type_count = 0
    for type in occurrences:
        if occurrences[type] > expected_type_count:
            expected_type_count = occurrences[type]
            expected_type = type
    col_obj.data_type = expected_type

    # Make the absolute values relative
    occurrences = make_dict_relative(occurrences, column_data.size)

    return occurrences


def export_json(filename, data):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4, sort_keys=True,
                  separators=(', ', ': '), ensure_ascii=False,
                  cls=NumpyEncoder)
    # with open(filename, 'w') as fp:
    #     json.dump(data, fp)


# input_file = "dwca-est_grey_seals_00-16-v1.1/event.txt"

def analyze(input_file):
    columns = []

    # reading csv file
    data = pd.read_csv(input_file, sep=predict_seperator(input_file))
    data_info = dict()  # Contains the info about each column

    # finding the type of each column
    for column in data:
        col_obj = Column(column)

        occurrences = dict()
        column_data = data[column]
        stats = dict()

        stats["type-occurrences"] = count_type_occurances(column_data, col_obj)

        col_obj.record_count = column_data.size
        col_obj.missing_count = int(stats["type-occurrences"]["empty"] * column_data.size)

        # There is nothing useful to say about most common nan's in an empty column
        if not stats["type-occurrences"]["empty"] == 1.0:
            stats["most-common"] = analyze_most_common(column_data)
            col_obj.common_values = stats["most-common"]

        if stats["type-occurrences"][index(bool)] or \
                stats["type-occurrences"][index(int)] or \
                stats["type-occurrences"][index(float)]:
            stats["avg"] = column_data.mean()
            col_obj.mean = stats["avg"]
            col_obj.median = column_data.median()
            stats["min"] = column_data.min()
            col_obj.min = stats["min"]
            stats["max"] = column_data.max()
            col_obj.max = stats["max"]
            stats["sd"] = column_data.std()  # Standard deviation

        if stats["type-occurrences"][index(str)]:
            str_lengths = [len(el) for el in column_data]
            stats["avg-length"] = 0 if len(str_lengths) == 0 else (float(sum(str_lengths)) / len(str_lengths))
            col_obj.mean = stats["avg-length"]
            col_obj.median = median(str_lengths)  # statistics.median
            stats["min-length"] = min(str_lengths)
            col_obj.min = stats["min-length"]
            stats["max-length"] = max(str_lengths)
            col_obj.max = stats["max-length"]
            stats["str-data"] = analyze_string_row(column_data)

        # Add a timestamp for when the last update was
        stats["timestamp"] = str(datetime.now())

        data_info[column] = stats

        columns.append(col_obj)

    # pprint(data_info)
    export_json("report.json", data_info)

    return columns
    # return data_info
