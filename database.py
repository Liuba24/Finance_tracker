import sqlite3

def init_db():
  connection = sqlite3.connect('finance.db')
  cursor = connection.cursor()
  
  #таблица транзакций
  cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      category TEXT NOT NULL,
      amount REAL NOT NULL,
      date TEXT NOT NULL,
      type TEXT NOT NULL
    )
  ''')
  
  #таблица бюджета
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
  connection.close()

#добавление транзакции
def add_transaction(category, amount, date, tr_type):
  connection = sqlite3.connect('finance.db')
  cursor = connection.cursor()

  cursor.execute('''
      INSERT INTO transactions (category, amount, date, type)
      VALUES (?, ?, ?, ?)''',
      (category, amount, date, tr_type)
  )

  connection.commit()
  connection.close()

#удаление транзакции
def delete_transaction(tr_id):
  connection = sqlite3.connect('finance.db')
  cursor = connection.cursor()
  cursor.execute(
    'DELETE FROM transactions WHERE id = ?',
    (tr_id,)
  )
  connection.commit()
  connection.close()

#установка бюджета на категорию 
def set_budget(category, period, budget_limit):
  connection = sqlite3.connect('finance.db')
  cursor = connection.cursor()
  cursor.execute('''
        INSERT OR REPLACE INTO budgets (category, period, budget_limit)
        VALUES (?, ?, ?)
    ''', (category, period, budget_limit)
  )
  connection.commit()
  connection.close()

#сколько ещё можно потратить по категории за этот месяц
def get_remaining_budget(category, period):
  connection = sqlite3.connect('finance.db')
  cursor = connection.cursor()
  cursor.execute('''
      SELECT budget_limit FROM budgets
      WHERE category = ? AND period = ?
  ''', (category, period))
  row = cursor.fetchone()
  limit_amount = row[0] if row else 0
  cursor.execute('''
      SELECT SUM(amount) FROM transactions
      WHERE category = ?
        AND type = 'Расход'
        AND substr(date, 1, 7) = ?
  ''', (category, period))
  spent_row = cursor.fetchone()
  spent = spent_row[0] if spent_row and spent_row[0] is not None else 0
  connection.close()
  return limit_amount - spent
