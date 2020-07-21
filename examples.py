
@app.route("/exampleMethod")
def exampleMethod():
    return "tests"


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
