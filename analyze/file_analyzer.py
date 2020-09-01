#
# Contains the main functionality for calling all the modules for the analyzing process
#
import pandas as pd
from .pandas_analyzer import analyze as analyze_data
from .hierarchical_analyzer import xml_to_dataframe, json_to_dataframe
from .unit_specific_analyzer import unit_specific_analyzer


def predict_csv_seperator(filename):
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

    file.close()
    return current_seperator


def get_file_data(file_location, extension):
    # Convert file to pandas frame
    if extension == "csv":
        return pd.read_csv(file_location, sep=predict_csv_seperator(file_location))
    elif extension == "xml":
        return xml_to_dataframe(file_location)
    elif extension == "json":
        return json_to_dataframe(file_location)
    else:
        print("File type not supported :-(")  # TODO: Should this raise an error or return empty list?
        return None


# returns a list of columns
def analyze_file(file_location, extension):
    data = get_file_data(file_location, extension)
    # Analyze the pandas frame
    print("\nAnalyzing file {}".format(file_location))
    result = analyze_data(data)
    return result

    # with open(file_location) as file:
    #     csv_analyzer.analyze(file)


# returns a string of unit specific information in JSON format
def reanalyze_file(file_location, extension, unitUri, column_name):
    # Put file into pandas dataframe
    data = get_file_data(file_location, extension)

    # Analyze the pandas frame
    print("\nReanalyzing file {}".format(file_location))
    
    return unit_specific_analyzer(unitUri, data[column_name])
