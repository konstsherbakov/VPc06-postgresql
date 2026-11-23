# PostgreSQL из Python — домашнее задание

Два уровня задания, каждый в своей папке со своим README и инструкцией запуска:

- [`basic/`](basic/) — базовый: подключение к PostgreSQL и вывод таблицы `users`.
- [`medium/`](medium/) — средний: таблицы `users` и `orders`, параметризованные запросы, транзакции, `LEFT JOIN + SUM`, проверка `ON DELETE CASCADE`, класс `PostgresDriver`.

Оба уровня работают с базой `test` на локальном PostgreSQL. Пароль хранится в `.env`, который исключён из репозитория (`.gitignore`); образец — `.env.example`.

Стек: Python 3, psycopg2-binary, python-dotenv, PostgreSQL, pgAdmin.
