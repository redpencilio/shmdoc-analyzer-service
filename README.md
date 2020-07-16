# shmdoc-analyzer-service

Microservice to derive scheme information and summary for different file formats.
Currently supported formats:
* `xml`
* `json`
* `csv`

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
