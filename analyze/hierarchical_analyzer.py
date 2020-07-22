import xmltodict
from pprint import pprint
import pandas
import json


def get_child_headers(child):
    children = set()
    if not isinstance(child, dict):
        return children
    for header in child:
        children.add(header)
    return children


# data should be list or dict
def children_same_columns(data):
    """
    Check if all children in the dict have the same column headers
    """
    child_headers = []
    for subcolumn in data:
        headers = ()
        if isinstance(data, dict):
            headers = get_child_headers(data[subcolumn])
        else:
            headers = get_child_headers(subcolumn)

        if len(headers) and headers in child_headers:
            return True
        child_headers.append(headers)
    return False


def find_longest_list(data):
    """
    In a nested dictionary, find the level with the most key/value-pairs
    """
    if not isinstance(data, (dict, list)):
        return []
    longest_list = data  # with length data
    for child in data:
        # if not isinstance(data[child], (dict, list)):
        #     continue
        ll_child = []
        if isinstance(data, dict):
            ll_child = find_longest_list(data[child])
        else:
            ll_child = find_longest_list(child)
        if len(ll_child) > len(longest_list) and children_same_columns(ll_child):
            longest_list = ll_child
    return longest_list


def normalize_to_longest_list(unnormalized):
    """
    Find the longest list in a nested dictionary (like the one obtained 
    from reading in a json file) with find_longest_list() and normalize/flatten 
    to this level.
    """
    longest_list = find_longest_list(unnormalized)
    normalized = pandas.json_normalize(longest_list)
    return normalized


def xml_to_dataframe(input_file):
    # Convert the xml file to a nested dictionary
    with open(input_file) as fd:
        # Dump in string and then reconvert to not have orderedDicts
        doc = json.dumps(xmltodict.parse(fd.read()))
    data = json.loads(doc)
    # Flatten the nested dictionary
    normalized = normalize_to_longest_list(data)
    return normalized


def json_to_dataframe(input_file):
    # Convert the json file to a nested dictionary
    with open(input_file) as fd:
        doc = fd.read()
    data = json.loads(doc)
    # Flatten the nested dictionary
    normalized = normalize_to_longest_list(data)
    return normalized
