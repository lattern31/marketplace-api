## Shopping cart API

## Запуск

* Заполнить файл .env на примере, env.example

### Докер

* Поднять контейнер и БД

```
make all
```

* Создать таблицы

```
alembic upgrade head
```

### Локально

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
