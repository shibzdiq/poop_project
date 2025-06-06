# Інформаційна система торгового центру

Веб-додаток для обліку магазинів, подій, оренди та обслуговування у торговому центрі. Реалізовано на Python (Flask), SQLite, Bootstrap.

## Основні можливості

- Додавання, редагування, видалення магазинів
- Ведення обліку власників, оренди, площі, статусу магазинів
- Управління подіями торгового центру (створення, редагування, видалення)
- Облік проблем з обслуговуванням (реєстрація, зміна статусу, історія)
- Пошук магазинів за різними критеріями
- Аутентифікація користувачів (адміністратор, користувач)

## Інструкція з запуску

1. Клонувати репозиторій та перейти у директорію проекту:
   ```bash
   git clone <repo-url>
   cd Назва Проєкту
   ```
2. Створити та активувати віртуальне середовище:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # або
   source venv/bin/activate  # Linux/Mac
   ```
3. Встановити залежності:
   ```bash
   pip install -r requirements.txt
   ```
4. Ініціалізувати базу даних:
   ```bash
   python init_db.py
   ```
5. Запустити сервер:
   ```bash
   python server.py
   ```
6. Відкрити у браузері: http://127.0.0.1:5000/

## Дефолтний адміністратор

- Email: admin@mall.com
- Пароль: admin

## Ліцензія

MIT
