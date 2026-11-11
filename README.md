# Web-Project
Веб-застосунок для трудомістких обчислень (СЛАР методом Гауса) з балансуванням навантаження: FastAPI, PostgreSQL, nginx, Docker Compose.

## Technologies 

- FastApi
...

## Architecture 

## Run app

Copy .env.example as .env

```
docker compose up --build -d

docker compose exec app alembic upgrade head
```