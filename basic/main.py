"""
Базовый уровень: подключение к PostgreSQL и чтение таблицы users.

Запуск:  python main.py
Параметры подключения берутся из файла .env (образец — .env.example).
"""

import os

import psycopg2
from dotenv import load_dotenv


def get_connection():
    """Открывает соединение с базой, параметры читает из переменных окружения."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


def main():
    # Загружаем переменные из .env в окружение процесса
    load_dotenv()

    conn = None
    try:
        conn = get_connection()
        print(f"Подключено к базе {os.getenv('DB_NAME')} на {os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}\n")

        with conn.cursor() as cur:
            cur.execute("SELECT id, name, age FROM users ORDER BY id;")
            rows = cur.fetchall()

        if not rows:
            print("Таблица users пуста — добавьте записи в pgAdmin.")
        else:
            print(f"{'id':<4} {'Имя':<20} Возраст")
            print("-" * 34)
            for user_id, name, age in rows:
                print(f"{user_id:<4} {name:<20} {age if age is not None else '—'}")
            print(f"\nВсего пользователей: {len(rows)}")

    except psycopg2.OperationalError as e:
        # Сервер не запущен, неверный пароль, нет такой базы и т. п.
        print("Не удалось подключиться к базе. Проверьте, что PostgreSQL запущен и данные в .env верные.")
        print(f"Подробности: {e}")
    except psycopg2.errors.UndefinedTable:
        print("Таблицы users нет в базе. Создайте её в pgAdmin — SQL в README.md.")
    except psycopg2.Error as e:
        # Остальные ошибки SQL
        print(f"Ошибка при работе с базой: {e}")
    finally:
        # Соединение закрываем в любом случае — и при успехе, и при ошибке
        if conn is not None:
            conn.close()
            print("Соединение закрыто.")


if __name__ == "__main__":
    main()
