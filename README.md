# Cайт Foodgram, «Продуктовый помощник»

## Описание

 На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд

## Технологии

**Python:** 3.11

**Django:** 4.2.2

## Проект на сервере

Проект доступен по адресу [158.160.25.190](http://158.160.25.190/)

Вход в админку:

admin@email.com

admin

## Шаблон наполнения env-файла

```python
SECRET_KEY=SECRET_KEY
DB_ENGINE=DB_ENGINE
DB_NAME=DB_NAME
POSTGRES_USER=POSTGRES_USER
POSTGRES_PASSWORD=POSTGRES_PASSWORD
DB_HOST=DB_HOST
DB_PORT=DB_PORT
SECRET_KEY=SECRET_KEY
DEBUG=DEBUG
ALLOWED_HOSTS ='host,host'
```

## Запуск приложения в контейнерах

- Перейдите в папку infra

    ```bash
    cd infra
    ```

- Запустите создание контейнеров

    ```bash
    docker-compose up
    ```

- Подготовьте миграции

    ```bash
    docker-compose exec backend python manage.py makemigrations reviews
    ```

- Выполните миграции

    ```bash
    docker-compose exec backend python manage.py migrate
    ```

- Создайте суперпользователя

    ```bash
    docker-compose exec backend python manage.py createsuperuser
    ```

- Соберите статику

    ```bash
    docker-compose exec web python manage.py collectstatic --no-input
    ```

- Проект доступен по адресу [http://localhost/](http://localhost/)

## Запуск проекта в dev-режиме

- Установите и активируйте виртуальное окружение  
    *для Windows:*  

    ```bash
    python -m venv venv
    source venv/Scripts/activate
    ```

    *для Linux и macOS:*

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

- Установите зависимости из файла requirements.txt

    ```bash
    pip install -r requirements.txt
    ```

- В папке с файлом manage.py выполните миграции:  
    *для Windows:*  

    ```bash
    python manage.py migrate
    ```

    *для Linux и macOS:*

    ```bash
    python3 manage.py migrate
    ```

- Запустите сервер:  
    *для Windows:*  

    ```bash
    python manage.py runserver
    ```

    *для Linux и macOS:*

    ```bash
    python3 manage.py runserver
    ```

## Примеры запросов к API

- Создайте пользователя

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"username": "MyUsername",
    "email ": "user@example.com", "first_name": "Вася", "last_name": "Пупкин", "password": "YourPassword"}' "/api/users/"
    ```

- Получите токен авторизации

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"password": "YourPassword", "email": "user@example.com"}' "api/auth/token/login/"
    ```

- Получите список всех рецептов:

    ```bash
    curl -X GET "/api/recipes/"
    ```

## Автор

- [Илий Дарья](https://github.com/DariaEaly)
