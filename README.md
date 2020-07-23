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
