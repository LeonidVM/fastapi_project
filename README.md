# 🚀 FastAPI URL Shortener

## 📂 Структура проекта

```
📦fastapi_project
 ┣ 📂fast_api_app
 ┃ ┣ 📜__init__.py
 ┃ ┣ 📜config.py
 ┃ ┣ 📜crud.py
 ┃ ┣ 📜database.py
 ┃ ┣ 📜keygen.py
 ┃ ┣ 📜main.py
 ┃ ┣ 📜models.py
 ┃ ┣ 📜schemas.py
 ┃ ┗ 📜telegram_bot.py
 ┣ 📜.gitignore
 ┣ 📜Dockerfile
 ┣ 📜requirements.txt
 ┗ 📜sql_database.db
```

## 📋 Описание модулей

| Модуль | Описание |
|--------|----------|
| **main.py** | API эндпоинты, логика приложения |
| **models.py** | Модели базы данных (SQLAlchemy) |
| **schemas.py** | Схемы валидации (Pydantic) |
| **crud.py** | CRUD операции и функции |
| **database.py** | Подключение к БД |
| **config.py** | Настройки приложения |
| **keygen.py** | Генерация уникальных ключей/ссылок |
| **telegram_bot.py** | Интеграция с тг ботом|

## ⚙️ Установка и запуск

### Локально
```bash
# 1. Клонировать
git clone git@github.com:LeonidVM/fastapi_project.git
cd fastapi_project

# 2. Виртуальное окружение
python -m venv venv
source venv/bin/activate  # или `venv\Scripts\activate` для Windows

# 3. Зависимости
pip install -r requirements.txt

# 4. Запуск
uvicorn fast_api_app.main:app --reload
```

## 📚 Документация API

После запуска доступна автоматическая документация:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
