# Project READ backend

## Setup

### Run the code

1. Clone the repo
2. Run `docker-compose up -d` in the project directory
3. Copy `.env.example` as `.env` in `projectread/` and add the environment variables
4. Go to `localhost:8000` to make sure everything works

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

1. Set up your local vault client by following the sections **Install the Vault Client** and **Point to our Vault server** in these [docs](https://www.notion.so/uwblueprintexecs/Secret-Management-2d5b59ef0987415e93ec951ce05bf03e#86337406f266493d990911901480f435)
2. Edit secrets in `./projectread/.env`
3. Update secrets by running
    ```bash
    vault kv get -format=json kv/project-read | python update_secret_files.py
    ```