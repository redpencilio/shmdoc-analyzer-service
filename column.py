import random
import string
import escape_helpers
import helpers

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
    return "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation,
                                                      value=escape_helpers.sparql_escape_string(value))
    # TODO: fix code below
    if value is not None and not isinstance(value, (bool, list)): # TODO: fix the bool and list
        return "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation, value=escape_helpers.sparql_escape(value))
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

    def query(self):
        base_uri = "http://example.com/columns/{id}".format(id=self.uuid)
        uri = escape_helpers.sparql_escape_uri(base_uri)

        query_str = "INSERT DATA { \n"
        query_str += "\tGRAPH {app_uri} {{ \n".format(app_uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/application"))
        query_str += "\t\t{uri} a ext:Column . \n".format(uri=uri)
        for attr, value in self.__dict__.items():
            print(attr, value, type(value))
            relation = get_relation(attr)
            query_str += str_query(uri, relation, value)
        query_str += "\t}"
        query_str += "}"

        prefixes = "PREFIX ext: {uri}\n".format(uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/ext/"))
        prefixes += "PREFIX mu: {uri}\n".format(uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/core/"))
        query_str = prefixes + query_str

        return query_str
