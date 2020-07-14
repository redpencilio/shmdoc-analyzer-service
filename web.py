import flask
import escape_helpers
from pprint import pprint
from .analyzer import analyze_file


# TODO: put example queries in seperate files

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

    location = result["results"]["bindings"][0]["file"]["value"]
    uri = escape_helpers.sparql_escape_uri(location)
    return uri


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

        SELECT (?uuid as ?id) ?logical_file ?format ?extension
        WHERE
        {{
            {uri} a nfo:FileDataObject ;
                  mu:uuid ?uuid .
            ?logical_file nie:dataSource {uri} .
            OPTIONAL {{ {uri} dct:format ?format }}
            OPTIONAL {{ {uri} dbpedia:fileExtension ?extension }}
        }}
        LIMIT 20
        """.format(uri=uri)

    result = helpers.query(file_query)
    pprint(flask.jsonify(result))

    logical_file = result["results"]["bindings"][0]["logical_file"]["value"]

    return logical_file


@app.route("/get_job_file/<uuid>")
def get_job_file(uuid):
    """
    Returns the properties of the created file (created/file URI)
    and the job uri.
    """
    uri = get_job_uri(uuid)
    logical_file = get_physical_file(uri)
    logical_file = logical_file.replace("share://", "/share/")
    return logical_file, uri


# zelfde formaat voor andere acties (naast 'run')
@app.route("/schema-analysis-jobs/<uuid>/run")
def run_job(uuid):
    """
    Queries job from database, gets file from job, reads file and processes
    """
    # Query job from database
    # Query file from database
    file_location, uri = get_job_file(uuid)
    # Read file
    # Processing
    result = analyze_file(file_location)
    # Write result to database columns
    pprint(result)

    return flask.jsonify(result)
    # Write results

