# Using Sqlalchemy with Flask, postgresql and Adminer in docker

First install docker in your computer

## Clone Project

```bash
git clone https://github.com/oyekamal/flask_SqlAlchemy_Postgress_docker.git
```

## Create python env

```bash
python3 -m venv venv
source venv/bin/activate
```

## Install packages

```bash
pip install -r requirements.txt
```

## Running the Postgres db

open another terminal. in order to run the Postgres in docker

```bash
cd postgres_docker
sudo docker-compose up
```

## Activating flask db

```bash
$ export FLASK_APP=app.py
$ flask run
$ flask db init
$ flask db migrate
$ flask db upgrade
```

## Check

open browser and search
<http://localhost:8080/>

select:

system : PostgreSQL

server: db

username: postgres

password: example

## Contributing

https://stackabuse.com/using-sqlalchemy-with-flask-and-postgresql/

https://www.bacancytechnology.com/blog/flask-jwt-authentication

## License

[MIT](https://choosealicense.com/licenses/mit/)
