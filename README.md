# shmdoc-analyzer-service

Microservice to derive scheme information and summary for different file formats.
Currently supported formats:
* `xml`
* `json`
* `csv`

This microservice is based on this [template](https://github.com/MikiDi/mu-python-template).

## Installation

Add the following snippet to your `docker-compose.yml` to include the file service in your project:
```yaml
shmdoc-analyzer:
  image: shmdoc/shmdoc-analyzer-service
  volumes:
    - ./data/files:/share
```

Add a rule to `dispatcher.ex` to dispatch all requests to start a `schema-analysis-job` at the service by using e.g. `/schema-analysis-job/job_id/run`. E.g.
```elixir
get "/schema-analysis-jobs/:id/run", _ do
  forward conn, [], "http://shmdoc-analyzer/schema-analysis-jobs/" <> id <> "/run"
end
```
The host `shmdoc-analyzer` in the forward URL reflects the name of the file service in the `docker-compose.yml` file.

More information on how to setup a mu.semte.ch project can be found in [mu-project](https://github.com/mu-semtech/mu-project).

A complete `docker-compose.yml` and `dispatcher.ex` file for running the entire shmdoc stack, can be found at the [app-shmdoc-osoc-poc repo](https://github.com/shmdoc/app-shmdoc-osoc-poc#shmdoc-poc-application).


## Development environment
For development, it is recommended to open up a port to the `shmdoc-analyzer-service`, so you don't have to access everything using the frontend.
This can be done by adding the following lines to your `docker-compose.dev.yml` file:
```yaml
services:
  shmdoc-analyzer:
    ports:
      - 8891:80
```
By doing this, you can directly access your Flask routes by going to `localhost:8801/route`, where `route` is the corresponding route. 
By default, the docker image will be loaded from [docker-hub](https://hub.docker.com/r/shmdoc/shmdoc-analyzer-service). While developing, you want to build your docker images from your own version of the repo. This can be done by adding the following lines in a `docker-compose.override.yml` file and passing the `--build` flag when running `docker-compose up`:
```yaml
services:
  shmdoc-analyzer:
    build: "../shmdoc-analyzer-service"
    volumes:
      - ./data/files:/share
    environment:
      MODE: "development"
```

Where `../shmdoc-analyzer-service` is the directory of this repo.

After doing this, you can run your development environment using:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.override.yml up --build
```

When you change things in python, Flask should restart automatically, so you can immediately run your newest code. If for some reason it doesn't restart, you can always restart the `shmdoc-analyzer-service` manually (but don't forget the extra docker-compose files then).

## Unittests
We've written a few tests for the service, but didn't find a good way to test them inside the docker container. So the way you can currently run the test is not the way you should do it, but we didn't find a better solution for now.

To run the tests, you can use:
```bash
python -m unittest tests/test.py 
```
Since you're not running this inside the docker-container, you should add the `escape_helpers.py` manually (and remove the import from `web.py` to prevent include loops). This file can be found in the [mu-python-service template](https://github.com/MikiDi/mu-python-template). As stated earlier, this is not the way you should actually do it, but no better way has been found.

## Running without Docker?
You should not do this, but it's often easier to use a debugger. You can do it similar as running the unittests, by having a copy of the helper files (and editting them to prevent import loops and other errors (which you get because you're not supposed to run it like this)). Once those are added, you can run `debug.py` with your favorite python debugger.
## How it works
We've used the [mu-python-service template](https://github.com/MikiDi/mu-python-template) for this microservice. This is based on Flask: incoming requests on port 80 get handled by the `web.py` file. Routes are defined by using the `@app.route("/route")` decorator from Flask. 
When using an IDE, you'll see objects like `app`, `helpers.py` and `escape_helpers.py` are missing. This is because the code should always be ran from a docker environment. 

## Other formats
The `file_analyzer` converts the files into a pandas dataframe and passes it to the `analyze` function, which returns the column objects.
If you want to support other formats, you can add a function to convert them to a pandas dataframe in the `file_analyzer` function.
For other formats, like SQL, the endpoint should pass them to a separate function (which is not yet implemented), that loads the data in a pandas dataframe (e.g. using `pandas.read_sql`), which can be passed to the `analyze` function.

## Queries to the database
Here you can find examples of how to insert objects to the database. 

You often don't want to wait for something to be implemented on the frontend to insert test data, so you can also manually execute database queries by going to `localhost:8890/sparql`, assuming the database service is mapped to port `8890`.

You can also use the `helpers.query` function to execute queries from python code.

### Uploading a file
This should happen using the file service, and not immediately accessing the database. This can be done with the following bash code:
```bash
curl -i -X POST -H "Content-Type: multipart/form-data" -F "file=@/a/file.somewhere" http://localhost/files
```
where `/a/file.somewhere` is the location of your file. This returns a json containing the file id. This will be used in the following queries. You can retrieve your uploaded files by going to `http://localhost/files`. You can also download a specific file by going to `http://localhost/files/<id>/download`.

### Create a schema-analysis-job
For a file with id `5f0c25c1936f81000c000000`, you can create a schema-analysis-job with id `1234` by running the following code on virtuoso (localhost:8890/sparql):
```sparksql
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>
PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

INSERT DATA {
  GRAPH <http://mu.semte.ch/application> {
    <http://example.com/schema-analysis-jobs/1234> a ext:SchemaAnalysisJob ;
                                                    mu:uuid "1234" ;
                                                    dct:created "1970-01-01T00:00:00"^^xsd:dateTime ;
                                                    ext:file  <http://mu.semte.ch/services/file-service/files/5f0c25c1936f81000c000000> .
  }
}
```
### Remove a schema-analysis-job
You can remove the schema-analysis-job with id `1234` and all it's relations by executing:
```
DELETE WHERE {
     GRAPH <http://mu.semte.ch/application> {
                <http://example.com/schema-analysis-jobs/1234> ?p ?o .
     }
}
```

### Removing all columns
Sometimes, while developing, you can get a lot of columns and want to remove them all. This can be done with the following query:
```sparksql
PREFIX ext: <http://mu.semte.ch/vocabularies/ext/>

DELETE WHERE {
     GRAPH <http://mu.semte.ch/application> {
                ?s a ext:Column .
                ?s ?r ?v .
     }
}
```