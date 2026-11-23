"""
postgres_driver.py — класс для работы с PostgreSQL: соединение, создание таблиц и CRUD.

Все запросы параметризованы (%s): значения передаются отдельно от текста SQL,
поэтому ввод не может изменить сам запрос (защита от SQL-инъекций).
Каждый метод выполняется в транзакции `with self.conn:` —
при успехе изменения фиксируются (commit), при ошибке откатываются (rollback).
"""

import os

import psycopg2


class PostgresDriver:
    def __init__(self):
        """Открывает соединение, параметры берёт из переменных окружения (.env)."""
        self.conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    def close(self):
        """Закрывает соединение. Безопасно вызывать повторно."""
        if self.conn is not None and not self.conn.closed:
            self.conn.close()

    # ---------- структура ----------

    def create_tables(self):
        """Создаёт таблицы users и orders, если их ещё нет."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id   SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    age  INT CHECK (age >= 0)
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id         SERIAL PRIMARY KEY,
                    user_id    INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    amount     NUMERIC(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)

    # ---------- пользователи ----------

    def add_user(self, name, age):
        """Добавляет пользователя и возвращает его id."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, age) VALUES (%s, %s) RETURNING id;",
                (name, age),
            )
            return cur.fetchone()[0]

    def find_user_id(self, name):
        """Возвращает id пользователя по имени или None, если такого нет."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE name = %s ORDER BY id LIMIT 1;", (name,))
            row = cur.fetchone()
            return row[0] if row else None

    def delete_user(self, user_id):
        """Удаляет пользователя. Его заказы удалятся автоматически (ON DELETE CASCADE)."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))

    # ---------- заказы ----------

    def add_order(self, user_id, amount):
        """Добавляет заказ пользователю и возвращает id заказа."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO orders (user_id, amount) VALUES (%s, %s) RETURNING id;",
                (user_id, amount),
            )
            return cur.fetchone()[0]

    def count_orders(self, user_id):
        """Сколько заказов у пользователя."""
        with self.conn, self.conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM orders WHERE user_id = %s;", (user_id,))
            return cur.fetchone()[0]

    # ---------- аналитика ----------

    def get_user_totals(self):
        """
        Сумма заказов по каждому пользователю.
        LEFT JOIN — чтобы в результат попали и пользователи без заказов (сумма 0).
        """
        with self.conn, self.conn.cursor() as cur:
            cur.execute("""
                SELECT u.name,
                       COALESCE(SUM(o.amount), 0) AS total_amount,
                       COUNT(o.id)                AS orders_count
                FROM users u
                LEFT JOIN orders o ON o.user_id = u.id
                GROUP BY u.id, u.name
                ORDER BY total_amount DESC, u.name;
            """)
            return cur.fetchall()
