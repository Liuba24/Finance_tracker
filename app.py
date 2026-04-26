import streamlit as st
from datetime import date
from database import add_transaction, init_db

init_db()
st.title('Добавление транзакции')
st.write('Заполните форму')

with st.form('add_transaction_form', clear_on_submit=True):
  category = st.text_input('Категория')
  amount = st.number_input('Бюджет на категорию')
  tran_date = st.date_input('Дата', value=date.today())
  tran_type = st.selectbox('Тип операции', ['Расход', 'Доход'])
  submit = st.form_submit_button("Добавить транзакцию")
if submit:
  if not category.strip():
    st.error("Заполните категорию")
  elif amount <= 0:
    st.error("Сумма должна быть положительной")
  else:
    date_str = str(tran_date)
    add_transaction(
      category=category.strip(),
      amount=float(amount),
      date=date_str,
      tr_type=tran_type
    )
    st.success(f"Транзакция '{category.strip()}' на сумму {amount:.2f} добавлена")