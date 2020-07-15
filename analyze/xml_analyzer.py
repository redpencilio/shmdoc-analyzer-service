import xmltodict
from pprint import pprint
import pandas
import json


def xml_to_dataframe(input_file):
    # Convert the xml file to a nested dictionary
    with open(input_file) as fd:
        doc = json.dumps(xmltodict.parse(fd.read()))

    data = json.loads(doc)

    # Flatten the nested dictionary
    normalized = pandas.json_normalize(data)

    for row in normalized:
        # TODO: zoek de kolom met de meeste rijen, want daarover willen we waarschijnlijk praten met shmdoc
        #  cause what it currently does is just take the data from the first row
        subdata = normalized[row]
        el = subdata[0]
        norm = pandas.json_normalize(el)
        return norm
    # normalized.to_csv("output.csv")

    # TODO: Should find all the lists with more than n rows (recursively)
    # # Get a csv of the creators
    # test = normalized["resource.creators.creator"]
    # el = test[0]
    # norm = pandas.json_normalize(el)
    # norm.to_csv("creators.csv")
    #
    # # pprint(normalized)
    # for element in normalized.iloc[:,-2]:
    #     for elementdeep in element:
    #         pprint(elementdeep)
