# сайт Foodgram, «Продуктовый помощник»

## Описание

 На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд

## Технологии

**Python:** 3.11

**Django:** 4.2.2

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
    curl -X GET "http://127.0.0.1:8000/api/recipes/"
    ```

## Автор

- [Илий Дарья](https://github.com/DariaEaly)
