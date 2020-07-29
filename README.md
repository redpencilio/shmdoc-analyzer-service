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
The host `shmdoc-analyzer` in the forward URL reflects the name of the analyzer service in the `docker-compose.yml` file.

More information on how to setup a mu.semte.ch project can be found in [mu-project](https://github.com/mu-semtech/mu-project).

A complete `docker-compose.yml` and `dispatcher.ex` file for running the entire shmdoc stack, can be found at the [app-shmdoc-osoc-poc repo](https://github.com/shmdoc/app-shmdoc-osoc-poc#shmdoc-poc-application).


## Development environment
For development, it is recommended to [open up](https://docs.docker.com/config/containers/container-networking/#published-ports) the port used by `shmdoc-analyzer-service`'s http-server', so you can access its endpoints directly instead of through the identifier and dispatcher.
This is provided for by the following lines in the project's [`docker-compose.dev.yml`](https://github.com/shmdoc/app-shmdoc-osoc-poc/blob/master/docker-compose.dev.yml) file:
```yaml
services:
  shmdoc-analyzer:
    ports:
      - 8891:80
```
By doing this, you can directly access your Flask routes by going to `localhost:8801/route`, where `route` is the corresponding route.  

By default, the code your service runs, is built into the docker image loaded from [docker-hub](https://hub.docker.com/r/shmdoc/shmdoc-analyzer-service). While developing, it is impractical to have to build a new image on each change. By virtue of Dockers' [volume mounting feature](https://docs.docker.com/storage/bind-mounts/), you can "mount" the application code that you are writing into the running container. This, combined with live-reload capability provided by the mu-semtech template, makes for a development setup that is always running your current code revision. Configuring the described setup can be achieved by adding following supplementary attributes to the `docker-compose.dev.yml`-configuration file :
```yaml
services:
  shmdoc-analyzer:
    volumes:
      - ../shmdoc-analyzer-service:/app
    environment:
      MODE: "development"
```

Where `../shmdoc-analyzer-service` is the directory of this repo. More info on this development-setup can be found in the [template's documentation](https://github.com/MikiDi/mu-python-template/#develop-a-microservice-using-the-template).

After doing this, you can run your development environment using:
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml -f docker-compose.override.yml up --build
```

When you change things in python, Flask should restart automatically, so you can immediately run your newest code. If for some reason it doesn't restart, you can always restart the `shmdoc-analyzer-service` manually (but don't forget the extra docker-compose files then).

## Unittests
We've written a few tests for the service, but didn't find a good way to test them inside the docker container. So the way you can currently run the test is not the way you should do it, but we didn't find a better solution for now.

You first have to manually setup your environment, which docker does automatically for u:
```bash
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
mv illegal/* .
```

To run the tests, you can use:
```bash
python -m unittest tests/test.py 
```
Since you're not running this inside the docker-container, you should add the `escape_helpers.py` manually (and remove the import from `web.py` to prevent include loops). This file can be found in the [mu-python-service template](https://github.com/MikiDi/mu-python-template), or the edited version of this file I've used while testing can be found in the `illegal` folder (which you have to copy to the project root). They can't be in the root by default, since this will give conflicts with the versions of these files you've got in the Docker container.  As stated earlier, this is not the way you should actually do it, but no better way has been found yet. In the future, it would make more sense to make the analyzer a seperate python package, independent from the Docker framework.

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
