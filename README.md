# Project READ backend 📚

Django backend for the GSL Hub. Check out the client code [here](https://github.com/uwblueprint/project-read-frontend)!

## Table of contents
  - [Setup](#setup)
    - [Requirements 📥](#requirements)
    - [Running the code 🏃](#running-the-code)
  - [Development workflow](#development-workflow)
    - [Accessing the Django admin 🗃](#accessing-the-django-admin)
    - [Generating seed data 🌱](#generating-seed-data)
    - [Installing new packages 📦](#installing-new-packages) 
    - [Database migrations 🗃](#database-migrations)
    - [Updating secrets 🔐](#updating-secrets)
    - [Testing ✅](#testing)
      - [Run automated tests](#run-automated-tests)
      - [Manual testing](#manual-testing)
    - [Linting 🧹](#linting)

## Setup

### Requirements
* [Docker](https://docs.docker.com/get-docker/)

### Running the code

1. Clone this repository and open the project folder:
   ```
   git clone https://github.com/uwblueprint/project-read-backend.git
   cd project-read-backend
   ```
1. Retrieve the environment variables & secrets from the team's Vault (shoutout to the Internal Tools team!).
   1. Follow these [docs](https://www.notion.so/uwblueprintexecs/Secret-Management-2d5b59ef0987415e93ec951ce05bf03e#a93b3e62a9a2459fa4990bf68b3dbc49) to get set up with Vault!
      - Skip the section *Create a GitHub team* – if you haven't been added to the Github team yet, message #project-read-devs on Slack.
      - For the section *Configure dev tools for your project repo*, setup.sh exists in /scripts, so run `./scripts/setup.sh` instead of `./setup.sh`.
   1. Pull the secrets into `.env`:
       ```
       vault kv get -format=json kv/project-read | python ./scripts/update_secret_files.py
       ```
1. Run the Docker container with `docker-compose up` in the project directory.
    * To run Docker in the background, run `docker-compose up -d` instead.
    * When you're done, run `docker-compose down` to stop the containers.
1. Go to [localhost:8000](http://localhost:8000/)! You should see a page that says "Api Root".

## Development workflow

### Accessing the Django admin

The [Django admin](https://docs.djangoproject.com/en/3.2/ref/contrib/admin/) provides a content management interface for us to manage our data. This will be helpful for doing manual testing, as you can create test data really easily!

1. Create a superuser under your Blueprint email:
   ```
   docker-compose exec web ./manage.py createsuperuser
   ```
1. Open [localhost:8080/admin](localhost:8080/admin) and sign in.

### Generating seed data

[This management command](https://github.com/uwblueprint/project-read-backend/blob/main/enrolments/management/commands/load_initial_data.py) will delete all existing records in your database, and populate it with randomly-generated seed data:
```bash
docker-compose exec web python manage.py load_initial_data
```

You can also specify the number of families, sessions, and classes per session to create:
```bash
docker-compose exec web python manage.py load_initial_data \
    --families X --sessions X --classes_per_session X
```

### Installing new packages

When adding new Python packages to the project, you'll need to define it as a dependency and rebuild the Docker container.

1. Install the packages and add them to `requirements.txt`:
    ```bash
    docker-compose exec web pip install [package]
    docker-compose exec web pip freeze > requirements.txt
    ```
1. Rebuild the container:
    ```bash
    docker-compose build
    docker-compose up -d
    ```

### Database migrations

When making changes to a `models.py` file, you may need to create a database migration so that other machines know to apply your changes. Here are some useful commands!

```bash
# Show existing migrations
docker-compose exec web ./manage.py showmigrations

# Make a new migrations file based on your changes to models.py
docker-compose exec web ./manage.py makemigrations

# Apply the migrations to your database
docker-compose exec web ./manage.py migrate
```

To migrate back to an old version:
```bash
docker-compose exec web ./manage.py migrate [app name] [migration name]

# ex. docker-compose exec web ./manage.py migrate accounts 0001_initial
```

To undo all migrations:
```bash
docker-compose exec web ./manage.py migrate [app name] zero
```
### Updating secrets

To pull the latest secrets from Vault:
```bash
vault kv get -format=json kv/project-read | python ./scripts/update_secret_files.py
```

To update our team secrets, see the [Vault docs](https://www.notion.so/uwblueprintexecs/Secret-Management-2d5b59ef0987415e93ec951ce05bf03e#3008f54889ab4b0cacfa276cbc43e613).

### Testing

#### Run automated tests

All automated tests need to pass before code can be merged:
```bash
docker-compose exec web ./manage.py test
```

#### Manual testing

To test authenticated endpoints locally, you'll need a token from our team's Firebase authentication server. If you don't yet have an account on our Firebase app, message #project-read-devs on Slack to get added!

1. Sync your Firebase user with your Django superuser, and retrieve a token:
    ```bash
    docker-compose exec web ./manage.py sync_firebase_user [email] [password]
    ```
    * This token expires after 60 minutes, at which point you should re-run this command to get a new one!
1. You can use this token and pass it as a bearer token for your API requests (using curl, Postman, etc).

### Lint

```bash
docker-compose exec web black .
```
