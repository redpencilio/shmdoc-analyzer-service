#
# Contains the main functionality for calling all the modules for the analyzing process
#
import pandas as pd
from .pandas_analyzer import analyze as analyze_data
from .hierarchical_analyzer import xml_to_dataframe, json_to_dataframe

# returns a list of columns
def analyze_database(parameters_still_todo):
    # Convert table to pandas frame
    data = None
    data = pd.read_sql(sql="todo", con="todo")
    data = pd.read_sql_query(sql="todo", con="todo")
    data = pd.read_sql_table(table_name="todo", con="todo")
    result = analyze_data(data)
    return result
