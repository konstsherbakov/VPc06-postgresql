# Базовый уровень — подключение к PostgreSQL из Python

`main.py` подключается к базе `test` через `psycopg2`, читает таблицу `users` и печатает её в консоль. Параметры подключения хранятся в `.env` и в репозиторий не попадают. Соединение закрывается в блоке `finally` при любом исходе.

## Подготовка базы (pgAdmin)

1. Создать базу `test`.
2. В Query Tool базы `test` выполнить:

```sql
CREATE TABLE IF NOT EXISTS users (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  age  INT  CHECK (age >= 0)
);
```

3. Через «Просмотр/редактирование данных» добавить минимум 3 записи и сохранить (F6).

## Запуск (Windows, PowerShell)

```
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

В файле `.env` указать свой пароль в `DB_PASSWORD`, затем:

```
python main.py
```

## Пример вывода

```
Подключено к базе test на localhost:5432

id   Имя                  Возраст
----------------------------------
1    Иван                 30
2    Мария                25
3    Пётр                 41

Всего пользователей: 3
Соединение закрыто.
```

## Обработка ошибок

- PostgreSQL не запущен или неверный пароль — понятное сообщение вместо падения программы.
- Нет таблицы `users` — подсказка создать её.
- В любом случае соединение закрывается в `finally`.
