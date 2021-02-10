# Project READ backend

## Setup

### Run the code

1. Clone the repo
2. Run `docker-compose up -d` in the project directory
3. Copy `.env.example` as `.env` in `projectread/` and add the environment variables
4. Go to `localhost:8000` to make sure everything works

When you're done, run `docker-compose down` to stop the containers.

### Open the Django admin

1. Create a superuser with `docker-compose exec web ./manage.py createsuperuser`
2. Open `localhost:8080/admin` and log in

## Installing new packages

1. Install the packages and add them to `requirements.txt`:
    ```bash
    docker-compose exec web pip install [package]
    docker-compose exec web pip freeze > requirements.txt
    ```
2. Rebuild the container:
    ```bash
    docker-compose build
    docker-compose up -d
    ```

## Migrations

```bash
# Show known migrations
docker-compose exec web ./manage.py showmigrations

# Make a new migrations file based on your changes to models.py
docker-compose exec web ./manage.py makemigrations

# Apply the migrations to your database
docker-compose exec web ./manage.py migrate
```

To migrate back to an old version:
```
docker-compose exec web ./manage.py migrate [app name] [migration name]

# ex. docker-compose exec web ./manage.py migrate accounts 0001_initial
```

## Lint

```
black .
```
