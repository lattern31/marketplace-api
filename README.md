## Shopping cart API
## Запуск 
* Заполнить файл .env на примере env.example (опционально)
* Поднять контейнеры
```
make all
```
* Создать таблицы
```
alembic revision --autogenerate && alembic upgrade head
```
