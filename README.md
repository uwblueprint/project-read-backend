# project-read-backend

# Setup

1. Clone the repo
2. Run `docker-compose up -d` in the project directory
3. Copy `.env.example` as `.env` in `projectread/` and add the environment variables
4. Go to `localhost:8000` to make sure everything works

When you're done, run `docker-compose down` to stop the containers.

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
