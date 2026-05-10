from database import add_transaction, set_budget, get_remaining_budget, delete_transaction
from models import Transaction, Budget
from database import delete_category_from_db

def process_delete_category(category_name: str) -> tuple[bool, str]:
    try:
        delete_category_from_db(category_name)
        return True, f"Категория '{category_name}' и связанный с ней бюджет успешно удалены."
    except Exception as e:
        return False, f"Ошибка при удалении: {str(e)}"
    

def process_new_transaction(tr: Transaction) -> tuple[bool, str]:
    """
    Записывает данные новой транзакции в базу данных и проверяет на корректность.
    Для транзакций типа 'Расход' проверяет остаток бюджета и возвращает 
    нужное предупреждение, если лимит превышен или близок к концу.
    """
    if not tr.category.strip():
        return False, "Заполните категорию"
    if tr.amount <= 0:
        return False, "Сумма должна быть положительной"
    
    if not isinstance(tr.date, str):
        tr.date = str(tr.date)
        
    add_transaction(tr)
    
    if tr.type == 'Расход':
        current_period = tr.date[:7]
        remaining = get_remaining_budget(tr.category.strip(), current_period)
        
        if remaining < 0:
            return True, f"Транзакция добавлена. Внимание! Вы превысили бюджет по категории '{tr.category}' на {-remaining} руб.!"
        elif 0 <= remaining <= 500:
            return True, f"Транзакция добавлена. Осторожно! По категории '{tr.category}' осталось всего {remaining} руб."
            
    return True, f"Транзакция '{tr.category.strip()}' на сумму {tr.amount:.2f} руб. добавлена!"


def process_new_budget(bud: Budget) -> tuple[bool, str]:
    """
    Валидирует данные и устанавливает новый лимит бюджета для указанной категории.
    """
    if not bud.category.strip():
        return False, "Заполните категорию"
    if bud.budget_limit < 0:
        return False, "Сумма должна быть положительной"
        
    set_budget(bud)
    return True, f"Бюджет {bud.budget_limit} руб. для категории '{bud.category}' на {bud.period} установлен!"


def process_delete_transaction(tr_id: int) -> tuple[bool, str]:
    """
    Проверяет переданный ID и удаляет транзакцию из базы данных.
    """
    if not tr_id:
         return False, "Не выбран ID транзакции"

    delete_transaction(tr_id)
    return True, "Транзакция успешно удалена!"
