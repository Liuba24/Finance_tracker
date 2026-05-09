import sqlite3
import pandas as pd
from typing import List
from models import Transaction, Budget

def init_db() -> None:
    """
    Инициализирует базу данных и создает необходимые таблицы, 
    если они не существуют
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()
        
        # Транзакции
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                type TEXT NOT NULL
            )
        ''')
        
        # Бюджет
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                budget_limit REAL NOT NULL,
                period TEXT NOT NULL,
                UNIQUE(category, period)
            )
        ''')
        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при инициализации БД: {e}")
    finally:
        if connection:
            connection.close()


def add_transaction(transaction: Transaction) -> None:
    """
    Добавляет новую транзакцию в базу данных.
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()

        cursor.execute('''
            INSERT INTO transactions (category, amount, date, type)
            VALUES (?, ?, ?, ?)''',
            (transaction.category, transaction.amount, transaction.date, transaction.type)
        )
        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при добавлении транзакции: {e}")
    finally:
        if connection:
            connection.close()


def delete_transaction(tr_id: int) -> None:
    """
    Удаляет транзакцию из базы данных по её идентификатору.
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM transactions WHERE id = ?", (tr_id,))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при удалении транзакции: {e}")
    finally:
        if connection:
            connection.close()


def set_budget(budget: Budget) -> None:
    """
    Устанавливает бюджет для категории
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO budgets (category, period, budget_limit)
            VALUES (?, ?, ?)
        ''', (budget.category, budget.period, budget.budget_limit))
        connection.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при установке бюджета: {e}")
    finally:
        if connection:
            connection.close()


def get_remaining_budget(category: str, period: str) -> float:
    """
    Рассчитывает остаток бюджета по категории за указанный период (год-месяц).
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()
        
        cursor.execute('''
            SELECT budget_limit FROM budgets
            WHERE category = ? AND period = ?
        ''', (category, period))
        row = cursor.fetchone()
        limit_amount = row[0] if row else 0.0
        
        cursor.execute('''
            SELECT SUM(amount) FROM transactions
            WHERE category = ?
              AND type = "Расход"
              AND substr(date, 1, 7) = ?
        ''', (category, period))
        spent_row = cursor.fetchone()
        spent = spent_row[0] if spent_row and spent_row[0] is not None else 0.0
        
        return float(limit_amount - spent)
    except sqlite3.Error as e:
        print(f"Ошибка при расчете остатка бюджета: {e}")
        return 0.0
    finally:
        if connection:
            connection.close()


def get_all_transactions() -> List[Transaction]:
    """
    Возвращает список всех транзакций из базы данных в виде объектов Transaction.
    """
    connection = None
    transactions_list = []
    try:
        connection = sqlite3.connect("finance.db")
        cursor = connection.cursor()
        
        cursor.execute("SELECT id, category, amount, date, type FROM transactions")
        rows = cursor.fetchall()
        
        for row in rows:
            transactions_list.append(
                Transaction(
                    id=row[0],
                    category=row[1],
                    amount=row[2],
                    date=row[3],
                    type=row[4]
                )
            )
    except sqlite3.Error as e:
        print(f"Ошибка при получении транзакций: {e}")
    finally:
        if connection:
            connection.close()
            
    return transactions_list


def get_expenses_dataframe() -> pd.DataFrame:
    """
    DataFrame со всеми расходами для аналитики.
    """
    connection = None
    try:
        connection = sqlite3.connect("finance.db")
        query = "SELECT category, amount, date FROM transactions WHERE type = 'Расход'"
        df = pd.read_sql(query, connection)
        return df
    except sqlite3.Error as e:
        print(f"Ошибка при получении данных для аналитики: {e}")
        return pd.DataFrame()
    finally:
        if connection:
            connection.close()
