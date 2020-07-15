import xmltodict
from pprint import pprint
import pandas
import json


def find_longest_list(data):
    longest_list = data  # with length data
    for child in data:
        if not isinstance(child, dict):
            continue
        ll_child = find_longest_list(data[child])
        if len(ll_child) > len(longest_list):
            longest_list = ll_child
    return longest_list


def xml_to_dataframe(input_file):
    # Convert the xml file to a nested dictionary
    with open(input_file) as fd:
        doc = json.dumps(xmltodict.parse(fd.read()))

    data = json.loads(doc)

    # Flatten the nested dictionary
    longest_list = find_longest_list(data)
    normalized = pandas.json_normalize(longest_list)
    return normalized
