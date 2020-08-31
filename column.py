import random
import string
import escape_helpers
import helpers
import numpy as np
import json
from datetime import datetime

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
                "common_values": "ext:commonValues",
                "file": "ext:file",
                "job": "ext:column"}

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

        uri_relations = (get_relation("data_type"))
        escaped_value = ""
        if relation in uri_relations:
            escaped_value = escape_helpers.sparql_escape_uri(value)
        else:
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

def extract_from_query(result, variable_to_extract: str):
    if variable_to_extract in result["results"]["bindings"][0].keys():
        return result["results"]["bindings"][0][variable_to_extract]["value"]
    else:
        return None



class Column:
    def get_column_by_uuid(self, uuid):
        """
        Queries the database for all the data of the column with given uuid
        """

        query = """
            PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
            PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
            PREFIX dct: <http://purl.org/dc/terms/>

            SELECT DISTINCT ?name, ?dataType, ?quantityKind, ?recordCount, ?missingCount, ?nullCount, ?min, ?max, ?mean, ?median, ?commonValues, ?unitSpecificInfo, ?unit, ?job{{
                GRAPH <http://mu.semte.ch/application> {{
                            ?column mu:uuid "{uuid}";
                                ext:name ?name;
                                ext:recordCount ?recordCount;
                                ext:missingCount ?missingCount;
                                ext:nullCount ?nullCount;
                                ext:min ?min;
                                ext:max ?max;
                                ext:mean ?mean;
                                ext:median ?median;
                                ext:commonValues ?commonValues.
                                ext:column ?job
                            OPTIONAL {{?columns ext:dataType ?dataType.}}.
                            OPTIONAL {{?columns ext:quantityKind ?quantityKind.}}.
                            OPTIONAL {{?columns ext:unitSpecificInfo ?unitSpecificInfo.}}.
                            OPTIONAL {{?columns ext:unit ?unit.}}.

                }}
            }}
            """.format(uuid=uuid)

        result = helpers.query(query)
        print("RESULT: ", result)

        self.name = extract_from_query(result, "name")    
        self.description = extract_from_query(result, "description")
        self.note = extract_from_query(result, "note")
        self.data_type = extract_from_query(result, "dataType")
        self.quantity_kind = extract_from_query(result, "quantityKind")
        self.unit = extract_from_query(result, "unit")
        self.record_count = extract_from_query(result, "recordCount")
        self.missing_count = extract_from_query(result, "missingCount")
        self.null_count = extract_from_query(result, "nullCount")
        self.min = extract_from_query(result, "min")
        self.max = extract_from_query(result, "max")
        self.mean = extract_from_query(result, "mean")
        self.median = extract_from_query(result, "median")
        self.common_values = extract_from_query(result, "commonValues")
        self.job = extract_from_query(result, "job")

    def __init__(self, name = None, uuid = None):
        """
        Two ways to iniialize this object:
            1. From an exiting column, then the uuid will not be none 
            and we will query the right column and fill in all fields
            2. It's a new column, the name wil then not be none and the 
            uuid is none
        """

        if (uuid is not None and name is None):
            self.uuid = uuid
            get_column_by_uuid(uuid)
        else:
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
            self.file = None
            self.job = None

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
            if relation == 'ext:file':
                str = "\t\t{uri} {relation} {value} . \n".format(uri=uri, relation=relation, value=value)
                query_str += str
            else:
                query_str += str_query(uri, relation, value)
        query_str += "{job} ext:column {column} . ".format(job=escape_helpers.sparql_escape_uri(job_uri), column=uri)
        query_str += """{uri} ext:finalized "{dateTime}"^^xsd:dateTime . """.format(uri=uri, dateTime=datetime.now().isoformat())
        query_str += "\t}\n"
        query_str += "}\n"

        prefixes = "PREFIX ext: {uri}\n".format(
            uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/ext/"))
        prefixes += "PREFIX mu: {uri}\n".format(
            uri=escape_helpers.sparql_escape_uri("http://mu.semte.ch/vocabularies/core/"))
        query_str = prefixes + query_str

        return query_str
