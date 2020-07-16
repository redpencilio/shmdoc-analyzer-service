import xmltodict
from pprint import pprint
import pandas
import json


def find_longest_list(data):
    """
    In a nested dictionary, find the level with the most key/value-pairs
    """
    longest_list = data  # with length data
    for child in data:
        if not isinstance(child, dict):
            continue
        ll_child = find_longest_list(data[child])
        if len(ll_child) > len(longest_list):
            longest_list = ll_child
    return longest_list


def normalize_to_longest_list(unnormalized):
    """
    Find the longest list in a nested dictionary (like the one obtained 
    from reading in a json file) with find_longest_list() and normalize/flatten 
    to this level.
    """
    longest_list = find_longest_list(data)
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
