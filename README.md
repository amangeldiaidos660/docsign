# DocSign

## Быстрый старт (локально)

1) Клонировать и создать venv
```
python -m venv venv
venv\Scripts\activate
```

2) Установить зависимости
```
pip install -r requirements.txt
```

3) Переменные окружения
Создайте `.env` в корне:
```
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/localdb
```

4) Подготовить БД
- Создайте базу `localdb` в PostgreSQL
- Запустите приложение один раз, чтобы включились расширения `pg_trgm` и `unaccent` (инициализируются в старте)

5) Миграции Alembic
```
# Применить существующие миграции
venv\Scripts\alembic.exe upgrade head

# Если изменились модели, то:
venv\Scripts\alembic.exe revision -m "message" --autogenerate
venv\Scripts\alembic.exe upgrade head
```

6) Запуск
```
python main.py
```
Откройте `http://localhost:8000`.

