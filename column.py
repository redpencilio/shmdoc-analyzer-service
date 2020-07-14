import random
import string
import escape_helpers

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
    return "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation, value=escape_helpers.sparql_escape_string(value))
    # TODO? Check whether value is defined?


class Column:
    def __init__(self, name):
        self.uuid = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
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
        uri = "<http://example.com/columns/{id}>".format(id=self.uuid)
        query_str = "INSERT DATA { \n"
        query_str += "\tGRAPH <http://mu.semte.ch/application> { \n"
        query_str += "\t\t{uri} a ext:Column . \n".format(uri=uri)
        for attr, value in self.__dict__.items():
            print(attr, value)
            relation = get_relation(attr)
            query_str += str_query(uri, relation, value)
        query_str += "\t}"
        query_str += "}"

        prefixes = "PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>\n"
        prefixes += "PREFIX mu: <http://mu.semte.ch/vocabularies/core/>\n"
        query_str = prefixes + query_str

        return query_str
