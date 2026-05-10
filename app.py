import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from database import get_expenses_dataframe, init_db, get_all_transactions, get_budget_categories
from services import process_new_transaction, process_new_budget, process_delete_transaction
from models import Transaction, Budget

init_db()

tab_set_budget, tab_add, tab_history, tab_analytics = st.tabs(["Установка бюджета", "Добавление транзакции", "История транзакций", "Аналитика"])

with tab_set_budget:
    st.title("Установите бюджет")
    st.write("Заполните форму")

    with st.form("add_budget", clear_on_submit=True):

        current_date = date.today()
        current_year = current_date.year
        current_month_str = current_date.strftime("%Y-%m")

        years = [current_year, current_year + 1]
        months = [f"{year}-{str(mon).zfill(2)}" for year in years for mon in range(1, 13)]

        default_index = months.index(current_month_str)

        budget = Budget(
            category=st.text_input("Категория"),
            period=st.selectbox("Период", options=months, index=default_index),
            budget_limit=st.number_input("Сумма", min_value=0.0)
            )

        submit = st.form_submit_button("Установить бюджет")

    if submit:
        success, message = process_new_budget(bud=budget)
        if success:
            st.success(message)
        else:
            st.error(message)

with tab_add:
    st.title("Добавление транзакции")

    budget_categories = get_budget_categories()
 
    if not budget_categories:
        st.warning("Нет доступных категорий. Пожалуйста, сначала установите бюджет хотя бы на одну категорию во вкладке 'Установка бюджета'.")
    else:
        st.write("Заполните форму")

        with st.form("add_transaction_form", clear_on_submit=True):
            tran = Transaction(
                category=st.selectbox("Категория", options=budget_categories),
                amount=st.number_input("Сумма операции", min_value=0.0),
                date=st.date_input("Дата", value=date.today()),
                type=st.selectbox("Тип операции", ["Расход", "Доход"])
            )
            submit = st.form_submit_button("Добавить транзакцию")
            
        if submit:
            success, message = process_new_transaction(tran)
            if success:
                if "Осторожно" in message:
                    st.warning(message)
                else:
                    st.success(message)
            else:
                st.error(message)

with tab_history:
    st.title("История транзакций")

    transactions = get_all_transactions()

    if not transactions:
        st.info("Нет транзакций")
    else:
        df_history = pd.DataFrame([
            {"ID" : tr.id,
             "Категория": tr.category,
             "Сумма": tr.amount,
             "Дата" : tr.date,
             "Тип": tr.type}
            for tr in transactions])
        
        st.subheader("Фильтры")
        col1, col2 = st.columns(2)

        with col1:
            type_filter = st.selectbox("Тип транзакции", ["Все", "Расход", "Доход"])

        with col2:
            categories = ["Все"] + list(df_history["Категория"].unique())
            category_filter = st.selectbox("Категория", categories)

        filtered_df = df_history.copy()

        if type_filter != "Все":
            filtered_df = filtered_df[filtered_df["Тип"] == type_filter]
        if category_filter != "Все":
            filtered_df = filtered_df[filtered_df["Категория"] == category_filter]

        st.dataframe(filtered_df, hide_index=True, use_container_width=True)

        st.subheader("Удаление транзакции")

        if not filtered_df.empty:
            options = {
                f"ID: {row['ID']} | {row['Дата']} | {row['Сумма']} руб. | {row['Категория']}": row['ID']
                for _, row in filtered_df.iterrows()
            }
            selected_option = st.selectbox("Выберите транзакцию для удаления:", list(options.keys()))
            
            if st.button("Удалить выбранную транзакцию"):
                tr_id_to_delete = options[selected_option]
                success, message = process_delete_transaction(tr_id_to_delete)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

with tab_analytics:
    st.title("Аналитика расходов")

    df = get_expenses_dataframe()

    if df.empty:
        st.info("Пока нет расходов для аналитики.")
    else:
        df["date"] = pd.to_datetime(df["date"])
        df["month"] = df["date"].dt.strftime("%Y-%m")
        all_months = sorted(df["month"].unique())
        
        if len(all_months) == 1:
            st.write(f"**Аналитика за:** {all_months[0]}")
            selected_month = all_months[0]
        else:
            selected_month = st.select_slider("Выберите месяц для анализа", options=all_months)

        filtered_df = df[df["month"] == selected_month]
        
        if filtered_df.empty:
            st.warning("В этом месяце нет расходов.")
        else:
            total_spent = filtered_df["amount"].sum()
            unique_days = filtered_df["date"].nunique()
            avg_per_day = total_spent / unique_days if unique_days > 0 else 0
            
            category_sum = filtered_df.groupby("category", as_index=False)["amount"].sum()
            top_category = category_sum.loc[category_sum["amount"].idxmax()]

            col1, col2, col3 = st.columns(3)
            col1.metric("Всего потрачено", f"{total_spent:.2f} руб.")
            col2.metric("В среднем за день", f"{avg_per_day:.2f} руб.")
            col3.metric("Самая затратная", f"{top_category["category"]}")

            fig_pie = px.pie(
                category_sum, 
                values="amount", 
                names="category", 
                title=f"Распределение расходов ({selected_month})"
            )
            st.plotly_chart(fig_pie)
            
            daily_sum = filtered_df.groupby("date", as_index=False)["amount"].sum()
            fig_bar = px.bar(
                daily_sum,
                x="date",
                y="amount",
                title="Динамика расходов по дням"
            )
            st.plotly_chart(fig_bar)