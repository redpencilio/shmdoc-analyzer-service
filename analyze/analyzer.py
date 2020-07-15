#
# Contains the main functionality for calling all the modules for the analyzing process
#
import pandas as pd
from .csv_analyzer import analyze as analyze_data
from .csv_analyzer import predict_seperator
from .xml_analyzer import xml_to_dataframe


# returns a list of columns
def analyze_file(file_location, extension):
    # reading csv file
    data = None
    if extension == "csv":
        data = pd.read_csv(file_location, sep=predict_seperator(file_location))
    elif extension == "xml":
        data = xml_to_dataframe(file_location)
    elif extension == "json":
        pass  # TODO
        return []
    else:
        print("File type not supported :-(")  # TODO: Should this raise an error or return empty list?
        return []
    result = analyze_data(data)
    return result

    # with open(file_location) as file:
    #     csv_analyzer.analyze(file)
