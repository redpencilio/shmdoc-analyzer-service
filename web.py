import flask
import escape_helpers
import helpers
from pprint import pprint
from .analyze.file_analyzer import analyze_file
from numpyencoder import NumpyEncoder

# from .tests.test import TestFile
import unittest

def get_job_uri(uuid):
    """
    Queries the database for SchemaAnalysisJob objects that
    have the uuid as specified by "uuid".
    """
    job_query = """
        PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
        PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
        PREFIX dct: <http://purl.org/dc/terms/>

        SELECT DISTINCT ?job, ?file, ?created WHERE {{
             GRAPH <http://mu.semte.ch/application> {{
                        ?job mu:uuid "{uuid}" ;
                        dct:created ?created ;
                         ext:file ?file ;
                           a ext:SchemaAnalysisJob.
             }}
        }}  OFFSET 0
            LIMIT 20
            """.format(uuid=uuid)

    result = helpers.query(job_query)

    file_uri = extract_from_query(result, "file")
    job_uri = extract_from_query(result, "job")

    return file_uri, job_uri


def extract_from_query(result, variable_to_extract: str):
    return result["results"]["bindings"][0][variable_to_extract]["value"]


def get_physical_file(uri):
    """
    Fetches the physical file on disk that belongs to a certain
    virtual file object (virtual files can link to files that are not in the
    database, but every file in the database has a virtual file object that acts
    as an identifier).
    """
    # Get file based on ?file
    file_query = """
        PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
        PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
        PREFIX dbpedia: <http://dbpedia.org/ontology/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>

        SELECT (?uuid as ?id) ?logical_file ?extension
        WHERE{{
            GRAPH <http://mu.semte.ch/application>{{
            {uri} a nfo:FileDataObject ;
                  dbpedia:fileExtension ?extension;
                  mu:uuid ?uuid .
            ?logical_file nie:dataSource {uri} .
            }}
        }}
        LIMIT 20
        """.format(uri=escape_helpers.sparql_escape_uri(uri))

    result = helpers.query(file_query)
    pprint(flask.jsonify(result))

    logical_file = extract_from_query(result, "logical_file")
    extension = extract_from_query(result, "extension")

    return logical_file, extension


def get_job_file(uuid):
    """
    Returns the properties of the created file (created/file URI)
    and the job uri.
    """
    file_uri, job_uri = get_job_uri(uuid)
    print("Job {} handles file {}".format(job_uri, file_uri))
    logical_file, extension = get_physical_file(file_uri)
    logical_file = logical_file.replace("share://", "/share/")
    return logical_file, file_uri, extension, job_uri


def add_column(column, uri):
    query = column.query(uri)
    print(query)
    helpers.query(query)


# zelfde formaat voor andere acties (naast 'run')
@app.route("/schema-analysis-jobs/<uuid>/run", methods=['GET','POST'])
def run_job(uuid):
    """
    Queries job from database, gets file from job, reads file and processes
    """
    print("Starting job with uuid", uuid)
    # Query job from database

    # TODO: code below is for files. When the job with given uuid contains a reference to an SQL database,
    #  you should pass it to the analyze function with a pandas dataframe
    #  (you can do this by using pandas.read_sql_table(...) or panda.read_sql(...)

    # Query file from database
    file_location, uri, extension, job_uri = get_job_file(uuid)
    # Read file
    # Processing
    result = analyze_file(file_location, extension)

    # Write result to database columns
    for column in result:
        add_column(column, job_uri)
    # pprint(result)

    # Resolve conflicts with jsonify of numpy i64
    app.json_encoder = NumpyEncoder
    return flask.jsonify({"Message": "You did it! The columns were succesfully added :-) Enjoy your day!",
                          "Note": "If you don't see anything added, it might be because there were no columns to do the analysis on or the file type is not supported"})
    # Write results
