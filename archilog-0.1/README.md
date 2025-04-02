# archilog

A simple project for educational purpose.

```bash
$ pdm run archilog
$ python -m  pdm run archilog display
$ pip install pdm
$ pdm run install
$ python -m pdm run archilog
$ python -m pdm run archilog create
$ python -m pdm run archilog init-db
$ python -m pdm add sqlalchemy
$ python -m pdm add flask (a la racine archilog-0.1)
$ python -m pdm add flask sqlalchemy click 
$ python -m pdm run flask --app archilog.routes routes
$ python -m pdm run archilog create --name "Alice" --amount 200 --category "Finance"
$ python -m pdm build
$ python -m pdm run start
$ python -m pdm add flask-httpauth
$ http://admin:wrongpassword@localhost:5000/
$ python -m pdm add spectree
$ python -m pdm add flask flask-httpauth pydantic spectree
$ python -m pdm add flask-jwt-extended


Usage: archilog [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  create
  delete
  get
  get-all
  import-csv
  init-db
  update
```

Course & examples : [https://kathode.neocities.org](https://kathode.neocities.org)