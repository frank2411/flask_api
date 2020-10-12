### Setup .env file with db connections

Example:

```shell
DB_ENGINE='postgresql+psycopg2'
DB_USER=postgres
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=5432
DB_NAME=worklife
```

### Run init-db and populate-db ( optional commands ) commands

```shell
flask init-db
flask populate-db
```

### Run the application

```shell
pipenv install
pipenv shell
flask run
```

### Run test suite

```shell
pipenv shell
tox
```

### Check swagger

go to: http://localhost:5000/api/v1/docs


### Additional info

Alembic is already configured to work out of the box. Without either flask-sqlalchemy and flask-migrate.





