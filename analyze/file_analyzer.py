#
# Contains the main functionality for calling all the modules for the analyzing process
#
import pandas as pd
from .pandas_analyzer import analyze as analyze_data
from .hierarchical_analyzer import xml_to_dataframe, json_to_dataframe


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

    return current_seperator


# returns a list of columns
def analyze_file(file_location, extension):
    # Convert file to pandas frame
    data = None
    if extension == "csv":
        data = pd.read_csv(file_location, sep=predict_csv_seperator(file_location))
    elif extension == "xml":
        data = xml_to_dataframe(file_location)
    elif extension == "json":
        data = json_to_dataframe(file_location)
    else:
        print("File type not supported :-(")  # TODO: Should this raise an error or return empty list?
        return []
    # Analyze the pandas frame
    result = analyze_data(data)
    return result

    # with open(file_location) as file:
    #     csv_analyzer.analyze(file)
