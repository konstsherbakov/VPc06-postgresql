"""
Средний уровень: таблицы users и orders, вставка данных из кода,
сумма заказов по пользователям (LEFT JOIN + SUM + GROUP BY)
и проверка ON DELETE CASCADE.

Запуск:  python main.py
Скрипт можно запускать повторно: демо-пользователи добавляются только один раз.
"""

import psycopg2
from dotenv import load_dotenv

from postgres_driver import PostgresDriver

# Демо-данные: имя, возраст, суммы заказов.
# У Веры заказов нет — она должна попасть в отчёт с суммой 0.00 благодаря LEFT JOIN.
DEMO_USERS = [
    ("Алиса", 28, [499.90, 1250.00]),
    ("Борис", 35, [3200.50]),
    ("Вера", 22, []),
    ("Глеб", 41, [150.00, 89.99, 760.00]),
]


def seed_demo_data(db):
    """Добавляет демо-пользователей и их заказы, если их ещё нет в базе."""
    added = 0
    for name, age, amounts in DEMO_USERS:
        if db.find_user_id(name) is not None:
            continue
        user_id = db.add_user(name, age)
        for amount in amounts:
            db.add_order(user_id, amount)
        added += 1
    if added:
        print(f"Добавлено демо-пользователей: {added}")
    else:
        print("Демо-пользователи уже есть в базе — повторно не добавляем.")


def check_cascade(db):
    """Создаёт временного пользователя с заказами, удаляет его и проверяет, что заказы исчезли."""
    print("\nПроверка ON DELETE CASCADE:")
    user_id = db.add_user("Временный пользователь", 30)
    db.add_order(user_id, 100.00)
    db.add_order(user_id, 200.00)
    print(f"  создан пользователь id={user_id}, заказов: {db.count_orders(user_id)}")
    db.delete_user(user_id)
    left = db.count_orders(user_id)
    print(f"  пользователь удалён, заказов осталось: {left}")
    print("  CASCADE работает: заказы удалены вместе с пользователем." if left == 0
          else "  Внимание: заказы остались — CASCADE не сработал.")


def print_totals(rows):
    """Печатает сумму заказов по пользователям в читабельном виде."""
    print("\nСумма заказов по пользователям (по убыванию):")
    width = max(len(name) for name, _, _ in rows)
    for name, total, count in rows:
        print(f"  {name:<{width}} — {total:>9.2f}  (заказов: {count})")


def main():
    load_dotenv()
    db = None
    try:
        db = PostgresDriver()
        db.create_tables()
        seed_demo_data(db)
        check_cascade(db)
        print_totals(db.get_user_totals())
    except psycopg2.OperationalError as e:
        print("Не удалось подключиться к базе. Проверьте, что PostgreSQL запущен и данные в .env верные.")
        print(f"Подробности: {e}")
    except psycopg2.Error as e:
        print(f"Ошибка при работе с базой: {e}")
    finally:
        if db is not None:
            db.close()
            print("\nСоединение закрыто.")


if __name__ == "__main__":
    main()
