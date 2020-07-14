#
# Contains the main functionality for calling all the modules for the analyzing process
#
from .csv_analyzer import analyze as analyze_csv

def analyze_file(file_location,extension):
    result = analyze_csv(file_location)
    return result

    # with open(file_location) as file:
    #     csv_analyzer.analyze(file)
