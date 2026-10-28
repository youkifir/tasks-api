# tasks-api

A minimal REST API for managing tasks, built with only the Python standard
library (`http.server` + `sqlite3`). No installation, no dependencies.

## Run

```bash
python -m tasks_api --port 8000
```

Data is stored in `tasks.db` (SQLite) next to where you run the command.

## Endpoints

| Method | Path          | Description                       |
|--------|---------------|-----------------------------------|
| GET    | `/tasks`      | List all tasks                    |
| POST   | `/tasks`      | Create a task `{"title": "..."}`  |
| GET    | `/tasks/{id}` | Get one task                      |
| PATCH  | `/tasks/{id}` | Update `title` and/or `done`      |
| DELETE | `/tasks/{id}` | Delete a task                     |

## Example

```bash
curl -X POST localhost:8000/tasks -d '{"title": "Buy milk"}'
# {"id": 1, "title": "Buy milk", "done": false}

curl -X PATCH localhost:8000/tasks/1 -d '{"done": true}'
curl localhost:8000/tasks
```

Errors return JSON, for example `{"error": "title is required"}` with
status 400, or 404 for unknown tasks.

## Tests

```bash
python -m unittest discover tests
```

## Ideas for extension

- Add authentication (API key or JWT)
- Rewrite on FastAPI or Flask and compare
- Add filtering (`/tasks?done=true`) and pagination
- Dockerfile for deployment

## License

MIT
