import random
import string
import escape_helpers
import helpers
import numpy as np
import json

relation_map = {"uuid": "mu:uuid",
                "name": "ext:name",
                "path": "ext:path",
                "description": "ext:description",
                "note": "ext:note",
                "disable_processing": "ext:disableProcessing",
                "data_type": "ext:dataType",
                "quantity_kind": "ext:quantityKind",
                "unit": "ext:unit",
                "record_count": "ext:recordCount",
                "missing_count": "ext:missingCount",
                "null_count": "ext:nullCount",
                "min": "ext:min",
                "max": "ext:max",
                "mean": "ext:mean",
                "median": "ext:median",
                "common_values": "ext:commonValues"}

def get_relation(attr_name):
    global relation_map
    return relation_map[str(attr_name)]


def str_query(uri, relation, value):
    if value is not None:
        if isinstance(value, list):
            # Store lists as json string dumps
            value = json.dumps(value)

        if type(value).__module__ == np.__name__:
            # Convert the numpy value (e.g. int64) to a python value
            value = value.item()
        escaped_value = escape_helpers.sparql_escape(value)

        if isinstance(value, bool):
            # Fix for weird problem with booleans
            escaped_value = escaped_value.replace("False", "false")
            escaped_value = escaped_value.replace("True", "true")
            escaped_value = escaped_value.replace("^^xsd:boolean",
                                                  "^^<http://mu.semte.ch/vocabularies/typed-literals/boolean>")

        return "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation,
                                                          value=escaped_value)
    return ""


class Column:
    def __init__(self, name):
        self.uuid = helpers.generate_uuid()
        self.name = name
        self.path = None
        self.description = None
        self.note = None
        self.disable_processing = False
        self.data_type = None
        self.quantity_kind = None
        self.unit = None
        self.record_count = None
        self.missing_count = None
        self.null_count = None
        self.min = None
        self.max = None
        self.mean = None
        self.median = None
        self.common_values = None

    def __repr__(self):
        return "<Column {} \"{}\">".format(self.record_count, self.name)

    def query(self, job_uri):
        base_uri = "http://example.com/columns/{id}".format(id=self.uuid)
        uri = escape_helpers.sparql_escape_uri(base_uri)

        query_str = "INSERT DATA { \n"
        query_str += "\tGRAPH {app_uri} {{ \n".format(
            app_uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/application"))
        query_str += "\t\t{uri} a ext:Column . \n".format(uri=uri)
        for attr, value in self.__dict__.items():
            print(attr, value, type(value))
            relation = get_relation(attr)
            query_str += str_query(uri, relation, value)
        query_str += "{job} ext:column {column} . ".format(job=escape_helpers.sparql_escape_uri(job_uri), column=uri)
        query_str += "\t}\n"
        query_str += "}\n"

        prefixes = "PREFIX ext: {uri}\n".format(
            uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/ext/"))
        prefixes += "PREFIX mu: {uri}\n".format(
            uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/core/"))
        query_str = prefixes + query_str

        return query_str
