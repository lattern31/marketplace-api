## Shopping cart API

### Локально

* Заполнить файл .env на примере, env.example

* Установить все зависимости через poetry и зайти в виртуальное окружение

```
poetry install && poetry shell
```

* Создать таблицы

```
alembic upgrade head
```

* Запуск

```
uvicorn --factory api.app:create_app
```
