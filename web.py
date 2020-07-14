import flask
import escape_helpers

# TODO: put example queries in seperate files
# Add run path to diespatcher.ex (same system as files/downloads)

def get_job_uri(uuid):
    """
    This function will query the database for SchemaAnalysisJob objects that
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
    This function fetches the physical file on disk that belongs to a certain
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
        """.format(uri=uri) # in value pythonstring, url moeten met <> gesp worden

    result = helpers.query(file_query)

    logical_file = result["results"]["bindings"][0]["logical_file"]["value"]

    return logical_file

@app.route("/get_job_file/<uuid>")
def get_job_file(uuid):
    """
    Returns the properties of the created file (created/file URI)
    """
    uri = get_job_uri(uuid)
    logical_file = get_physical_file(uri)
    logical_file = logical_file.replace("share://", "/share/")
    file = open(logical_file)
    file_text = file.read()
    return file_text
    return flask.jsonify(result)


def get_file(uri):
    # Returns the file located at the given uri
    return str(uri)

# zelfde formaat voor andere acties (naast 'run')
@app.route("/schema-analysis-jobs/<uuid>/run")
def run_job(uuid):
    # Query job uit database
    # Query file uit database
    # File uitlezen
    # Processing
    # Resultaten wegschrijven
    pass

# @app.route("/analysis/<uuid>/run")
# def run_job(uuid):
#     job = get_job(uuid)
#     return get_file(job[0])


@app.route("/exampleMethod")
def exampleMethod():
    return "test"


@app.route("/exampleQuery")
def exampleQuery():
    example_query = """PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
        PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
        PREFIX dbpedia: <http://dbpedia.org/ontology/>
        PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>

        SELECT DISTINCT (?virtualFile AS ?uri) (?physicalFile AS ?physicalUri) (?uuid as ?id) ?name ?extension
        WHERE {
            ?virtualFile a nfo:FileDataObject ;
                mu:uuid ?uuid .
            ?physicalFile a nfo:FileDataObject ;
                nie:dataSource ?virtualFile .
            ?virtualFile nfo:fileName ?name .
            ?virtualFile dbpedia:fileExtension ?extension .
        }"""

    return flask.jsonify(helpers.query(example_query))


@app.route("/test2")
def test2():
    f = open("/share/5f0c25efd7814c000c000001.xml")
    s = ""
    for line in f:
        s += line + "\n"
    f.close()
    return s
