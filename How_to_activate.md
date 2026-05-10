## Как запустить проект локально

1. Склонируйте [репозиторий](https://github.com/Liuba24/Finance_tracker) и перейдите в папку проекта.
2. Создайте виртуальное окружение:
   ```bash
   python -m venv venv
   ```
3. Активируйте виртуальное окружение:
   - Для Windows: `venv\Scripts\activate`
   - Для Mac/Linux: `source venv/bin/activate`
4. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
5. Запустите приложение:
   ```bash
   streamlit run app.py
   ```