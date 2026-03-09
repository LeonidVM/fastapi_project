## 🚀 FastAPI Проект для сокращения ссылок

Для начала, посмотрим на структуру проекта:

### 📂 Структура проекта

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

## Демонстрация функций

Демонстрация всего, что есть в Swagger UI:

<img width="1107" height="577" alt="Снимок экрана 2026-03-09 в 15 53 21" src="https://github.com/user-attachments/assets/a7e0afcf-e75f-401b-96f9-f61dba7f8381" />

Посмотрим что умеет наш проект, начнем с пяти обязательных функций:

## 1) Создание / удаление / изменение / получение информации по короткой ссылке:

Вставляем длинную ссылку: 
<img width="1094" height="264" alt="Снимок экрана 2026-03-09 в 16 06 08" src="https://github.com/user-attachments/assets/3fe543bd-fbf1-4d2b-a0d7-259ff0d286ab" />

На выходе получаем две короткие ссылки, обычную и для админа:
<img width="995" height="128" alt="Снимок экрана 2026-03-09 в 16 06 27" src="https://github.com/user-attachments/assets/6543f5f0-2cfa-4d87-b54b-2fef65af1f51" />

Обе эти ссылки работают, по ним можно перейти

Также по сокращенному коду можно изменить (обновить) ссылку:
<img width="1089" height="202" alt="Снимок экрана 2026-03-09 в 16 07 15" src="https://github.com/user-attachments/assets/3f9d7324-2d04-4a39-896e-041fc6ce0e2e" />

На выходе получаем новую ссылку с другим кодом:
<img width="992" height="127" alt="Снимок экрана 2026-03-09 в 16 07 29" src="https://github.com/user-attachments/assets/f2428257-617e-4648-a753-4a52c77e8bf0" />

Наконец, эту ссылку можно удалить:
<img width="1081" height="198" alt="Снимок экрана 2026-03-09 в 16 08 04" src="https://github.com/user-attachments/assets/904954e1-1bff-458d-9317-4223802d39b6" />

<img width="991" height="88" alt="Снимок экрана 2026-03-09 в 16 08 12" src="https://github.com/user-attachments/assets/ec858302-e952-4941-a519-26f4f3219229" />

Все, ссылка удалена, теперь по ней не получится перейти

## 2) Статистика по ссылке:

По каждой ссылке можно посмотреть статистику, а именно:
- Оригинальная ссылка (target_url)
- Время создания (created_at)
- Время последнего перехода по ссылке (last_used)
- Количество переходов (clicks)
- Время, до которого ссылка валидна (expires_at, пригодится в п.5 для срока жизни ссылки) 

Сгенерируем новую ссылку и посмотрим в действии.
Вставили сгенерированный код:
<img width="1079" height="269" alt="Снимок экрана 2026-03-09 в 16 17 26" src="https://github.com/user-attachments/assets/26735608-03ae-466b-87b5-3ddfc5028ee9" />
И получили статистику:
<img width="987" height="140" alt="Снимок экрана 2026-03-09 в 16 17 39" src="https://github.com/user-attachments/assets/8d8c50d0-3b45-4b97-9248-e22f71af4982" />

Видно, что ссылка создана только что.
Подождем пару минут и несколько раз перейдем по ссылке, посмотрим, что изменится:
<img width="996" height="142" alt="Снимок экрана 2026-03-09 в 16 19 34" src="https://github.com/user-attachments/assets/b0eb11d4-cb7c-48b9-85bf-fbf05b688994" />

Видно, что параметр clicks увеличился до 4, а также изменилось время последнего использования. Все работает.

## 3) Создание кастомных ссылок

До этого сокращенная ссылка создавалась благодаря рандомному уникальному коду. Однако пользователи могут также придумывать свои кастомные алиасы. Для этого вводим целевую ссылку и алиас, на который мы хотим ее заменить. Посмотрим как это работает:
<img width="1087" height="273" alt="Снимок экрана 2026-03-09 в 16 27 19" src="https://github.com/user-attachments/assets/e0ea05e8-98f9-4771-af33-0213fddfdfc9" />

Получаем такой результат:
<img width="982" height="150" alt="Снимок экрана 2026-03-09 в 16 27 29" src="https://github.com/user-attachments/assets/178e01fd-9baf-4927-b0f3-6b4eef580449" />

Все, ссылка с алиасом fly_fly создана и работает. По ней также можно считать статистику, удалять и тд. На алиас наложены определенные ограничения: длина от 4 до 20 символов, можно использовать только буквы, цифры, дефис и нижнее подчеркивание, начинаться должен с буквы/цифры





### ⚙️ Установка и запуск

#### Локально
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
