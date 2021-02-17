# Project READ backend

## Setup

### Run the code

1. Clone the repo
2. Run `docker-compose up -d` in the project directory
3. Copy `.env.example` as `.env` in `projectread/`
4. Follow these [docs](https://www.notion.so/uwblueprintexecs/Secret-Management-2d5b59ef0987415e93ec951ce05bf03e#a93b3e62a9a2459fa4990bf68b3dbc49) to set up with vault.  
    Notes on setup:
    - Ignore the section *Create a GitHub team* since we already have a team set up
    - For the section *Configure dev tools for your project repo*, setup.sh exists in /scripts, so make sure to run ./scripts/setup.sh instead of ./setup.sh
5. Pull secrets into `.env` by running
    ```bash
    vault kv get -format=json kv/project-read | python ./scripts/update_secret_files.py
    ```
6. Go to `localhost:8000` to make sure everything works

When you're done, run `docker-compose down` to stop the containers.

### Open the Django admin

1. Open a shell with `docker-compose run web bash`
2. Create a superuser with `python manage.py createsuperuser`
3. Open `localhost:8080/admin` and log in

## Installing new packages

1. Open a shell with `docker-compose run web bash`
2. Install the packages and add them to `requirements.txt`:
    ```bash
    pip install [package]
    pip freeze > requirements.txt
    ```
3. Rebuild the container:
    ```bash
    docker-compose build
    docker-compose up -d
    ```

## Lint

```
docker-compose run web bash
black .
```

## Updating Secrets
If you have not set up secrets management, please refer to steps 4 and 5 in the *Run the code* section of this README.