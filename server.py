# Імпорт необхідних бібліотек для роботи Flask-додатку, роботи з БД та формами
from flask import render_template
import sqlite3
# import requests
from flask import Flask, request, redirect, url_for, session, flash
from flask_wtf import FlaskForm
from wtforms import StringField
from datetime import datetime

# Створення Flask-додатку
app = Flask(__name__)
# Секретний ключ для сесій
app.secret_key = "super secret key"

# Головна сторінка, ініціалізація БД та перенаправлення на /index
@app.route('/')
def hel():
    # Відкриваємо базу даних
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")
    
    # Створення таблиці магазинів, якщо не існує
    conn.execute('''CREATE TABLE IF NOT EXISTS stores 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT,
         category TEXT,
         floor INTEGER,
         area REAL,
         owner_name TEXT,
         owner_phone TEXT,
         owner_email TEXT UNIQUE,
         rent_start_date TEXT,
         rent_end_date TEXT,
         monthly_rent REAL,
         status TEXT)''')
    
    # Створення таблиці користувачів (адміністраторів ТЦ)
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         name TEXT,
         email TEXT UNIQUE,
         password TEXT,
         role TEXT,
         phone TEXT)''')
    
    # Створення таблиці обслуговування
    conn.execute('''CREATE TABLE IF NOT EXISTS maintenance 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         store_id INTEGER,
         issue_type TEXT,
         description TEXT,
         reported_date TEXT,
         status TEXT,
         resolved_date TEXT,
         FOREIGN KEY (store_id) REFERENCES stores(id))''')
    
    # Створення таблиці подій
    conn.execute('''CREATE TABLE IF NOT EXISTS events 
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         title TEXT,
         description TEXT,
         start_date TEXT,
         end_date TEXT,
         location TEXT,
         status TEXT)''')
    
    print("Tables created successfully")
    conn.close()
    
    # Перевірка, чи є користувач у сесії
    if session.get('username')==True:
        messages = session['username']
    else:
        messages = ""
    user = {'username': messages}
    # Перенаправлення на сторінку index
    return redirect(url_for('index',user=user))

# Сторінка реєстрації користувача
@app.route('/reg')
def add():
    return render_template('register.html')

# Додавання нового користувача до БД (реєстрація)
@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    msg = ""
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            password = request.form['password']
            role = 'user'
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                # Перевірка, чи існує вже користувач з таким email
                cur.execute("SELECT * FROM users WHERE email=?", (email,))
                if cur.fetchone():
                    flash('Користувач з таким email вже існує!')
                    return redirect(url_for('add'))
                # Додавання нового користувача
                cur.execute("INSERT INTO users (name, email, password, role, phone) VALUES (?, ?, ?, ?, ?)",
                            (name, email, password, role, phone))
                con.commit()
                flash('Реєстрація успішна! Тепер увійдіть у систему.')
                return redirect(url_for('login'))
        except Exception as e:
            con.rollback()
            msg = f'Помилка при реєстрації: {str(e)}'
            flash(msg)
            return redirect(url_for('add'))
    return redirect(url_for('add'))

# Головна сторінка зі списком магазинів та пошуком
@app.route('/index',methods = ['POST','GET'])
def index():
    if request.method == 'POST':
        if session.get('username') is not None:
            messages = session['username']
        else:
            messages = ""
        user = {'username': messages}
        search_term = request.form['search']
        search_type = request.form['type']
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        # Пошук магазинів за різними параметрами
        if search_type == 'store_name':
            cur.execute("SELECT * FROM stores WHERE name LIKE ?", ('%' + search_term + '%',))
            search_results = cur.fetchall()
        elif search_type == 'category':
            cur.execute("SELECT * FROM stores WHERE category LIKE ?", ('%' + search_term + '%',))
            search_results = cur.fetchall()
        elif search_type == 'owner':
            cur.execute("SELECT * FROM stores WHERE owner_name LIKE ?", ('%' + search_term + '%',))
            search_results = cur.fetchall()
        cur.execute("SELECT * FROM stores")
        all_stores = cur.fetchall()
        # Якщо пошук не дав результатів — показати всі магазини
        if not search_results:
            search_results = all_stores
        return render_template('index.html', 
                             title='Mall Management System', 
                             user=user,
                             stores=all_stores,
                             search_results=search_results)
    if session.get('username') is not None:
        messages = session['username']
    else:
        messages = ""
    user = {'username': messages}
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM stores")
        stores = cur.fetchall()
        return render_template('index.html', 
                             title='Mall Management System', 
                             user=user, 
                             stores=stores)

# Сторінка зі списком користувачів
@app.route('/list')
def list():
   con = sqlite3.connect('database.db')
   con.row_factory = sqlite3.Row
   cur = con.cursor()
   cur.execute("select * from users")
   rows = cur.fetchall();
   print(rows)
   return render_template("list.html",rows = rows)

# Видалення таблиці request (для тестування)
@app.route('/drop')
def dr():
        con = sqlite3.connect('database.db')
        con.execute("DROP TABLE request")
        return "dropped successfully"

# Сторінка входу користувача
@app.route('/login',methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('/login.html')
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        # Вхід для адміністратора
        if email == 'admin@mall.com' and password == 'admin':
            session['username'] = email
            session['admin'] = True
            session['role'] = 'admin'
            return redirect(url_for('index'))
        # Вхід для звичайного користувача
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email=?", (email,))
        user = cur.fetchone()
        
        if user and user['password'] == password:
            session['username'] = email
            session['logged_in'] = True
            session['role'] = user['role']
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password')
            return render_template('/login.html')
            
    return render_template('/login.html')

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   session.pop('logged_in',None)
   try:
       session.pop('admin',None)
   except KeyError as e:
       print("I got a KeyError - reason " +str(e))

   return redirect(url_for('login'))

@app.route("/editstore/<id>", methods=('GET', 'POST'))
def editstore(id):
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM stores WHERE id=?", (id,))
        store = cur.fetchone()
        return render_template("editstore.html", store=store)
        
    if request.method == 'POST':
        try:
            store_name = request.form['store_name']
            category = request.form['category']
            floor = request.form['floor']
            area = request.form['area']
            owner_name = request.form['owner_name']
            owner_phone = request.form['owner_phone']
            owner_email = request.form['owner_email']
            rent_start = request.form['rent_start']
            rent_end = request.form['rent_end']
            monthly_rent = request.form['monthly_rent']
            status = request.form['status']
            # Перевірка дат оренди
            if rent_end < rent_start:
                flash('Кінець оренди не може бути раніше за початок оренди!')
                return redirect(url_for('editstore', id=id))
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""UPDATE stores SET 
                    name=?, category=?, floor=?, area=?, owner_name=?, 
                    owner_phone=?, owner_email=?, rent_start_date=?, 
                    rent_end_date=?, monthly_rent=?, status=? 
                    WHERE id=?""",
                    (store_name, category, floor, area, owner_name,
                    owner_phone, owner_email, rent_start, rent_end,
                    monthly_rent, status, id))
                con.commit()
                flash('Store information updated successfully')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error updating store: {str(e)}')
            return redirect(url_for('editstore', id=id))

@app.route('/events')
def events():
    # Доступ дозволено всім (і неавторизованим)
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM events ORDER BY start_date DESC")
    events = cur.fetchall()
    return render_template('events.html', events=events)

@app.route('/addevent', methods=['GET', 'POST'])
def addevent():
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            location = request.form['location']
            status = 'Upcoming'

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO events 
                    (title, description, start_date, end_date, location, status) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (title, description, start_date, end_date, location, status))
                con.commit()
                flash('Event added successfully')
                return redirect(url_for('events'))
        except Exception as e:
            flash(f'Error adding event: {str(e)}')
            return redirect(url_for('addevent'))
            
    return render_template('addevent.html')

@app.route('/editevent/<id>', methods=['GET', 'POST'])
def editevent(id):
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    if request.method == 'GET':
        con = sqlite3.connect('database.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM events WHERE id=?", (id,))
        event = cur.fetchone()
        return render_template('editevent.html', event=event)
        
    if request.method == 'POST':
        try:
            title = request.form['title']
            description = request.form['description']
            start_date = request.form['start_date']
            end_date = request.form['end_date']
            location = request.form['location']
            status = request.form['status']

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""UPDATE events SET 
                    title=?, description=?, start_date=?, end_date=?, 
                    location=?, status=? WHERE id=?""",
                    (title, description, start_date, end_date, 
                    location, status, id))
                con.commit()
                flash('Event updated successfully')
                return redirect(url_for('events'))
        except Exception as e:
            flash(f'Error updating event: {str(e)}')
            return redirect(url_for('editevent', id=id))

@app.route('/deleteevent/<id>')
def deleteevent(id):
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("DELETE FROM events WHERE id=?", (id,))
        con.commit()
        flash('Event deleted successfully')
    except Exception as e:
        flash(f'Error deleting event: {str(e)}')
    return redirect(url_for('events'))

@app.route('/maintenance')
def maintenance():
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("""
        SELECT m.*, s.name as store_name 
        FROM maintenance m 
        JOIN stores s ON m.store_id = s.id 
        ORDER BY m.reported_date DESC
    """)
    maintenance_issues = cur.fetchall()
    return render_template('maintenance.html', maintenance_issues=maintenance_issues)

@app.route('/addmaintenance', methods=['GET', 'POST'])
def addmaintenance():
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        try:
            store_id = request.form['store_id']
            issue_type = request.form['issue_type']
            description = request.form['description']
            reported_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            status = 'Pending'

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO maintenance 
                    (store_id, issue_type, description, reported_date, status) 
                    VALUES (?, ?, ?, ?, ?)""",
                    (store_id, issue_type, description, reported_date, status))
                con.commit()
                flash('Maintenance issue reported successfully')
                return redirect(url_for('maintenance'))
        except Exception as e:
            flash(f'Error reporting maintenance issue: {str(e)}')
            return redirect(url_for('addmaintenance'))
            
    # Get list of stores for the form
    con = sqlite3.connect('database.db')
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("SELECT id, name FROM stores WHERE status != 'Inactive'")
    stores = cur.fetchall()
    return render_template('addmaintenance.html', stores=stores)

@app.route('/updatemaintenance/<id>', methods=['POST'])
def updatemaintenance(id):
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    try:
        status = request.form['status']
        resolved_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') if status == 'Resolved' else None

        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("""UPDATE maintenance SET 
                status=?, resolved_date=? WHERE id=?""",
                (status, resolved_date, id))
            con.commit()
            flash('Maintenance status updated successfully')
    except Exception as e:
        flash(f'Error updating maintenance status: {str(e)}')
    return redirect(url_for('maintenance'))

@app.route('/deletemaintenance/<id>')
def deletemaintenance(id):
    if not session.get('admin'):
        flash('Access denied. Admin privileges required.')
        return redirect(url_for('index'))
        
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        cur.execute("DELETE FROM maintenance WHERE id=?", (id,))
        con.commit()
        flash('Maintenance record deleted successfully')
    except Exception as e:
        flash(f'Error deleting maintenance record: {str(e)}')
    return redirect(url_for('maintenance'))

@app.route('/addstore', methods=['GET', 'POST'])
def addstore():
    if not session.get('admin'):
        flash('Доступ заборонено. Потрібні права адміністратора.')
        return redirect(url_for('index'))
    if request.method == 'POST':
        try:
            store_name = request.form['store_name']
            category = request.form['category']
            floor = request.form['floor']
            area = request.form['area']
            owner_name = request.form['owner_name']
            owner_phone = request.form['owner_phone']
            owner_email = request.form['owner_email']
            rent_start = request.form['rent_start']
            rent_end = request.form['rent_end']
            monthly_rent = request.form['monthly_rent']
            status = 'Active'
            # Перевірка дат оренди
            if rent_end < rent_start:
                flash('Кінець оренди не може бути раніше за початок оренди!')
                return redirect(url_for('addstore'))
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("""INSERT INTO stores \
                    (name, category, floor, area, owner_name, owner_phone, \
                    owner_email, rent_start_date, rent_end_date, monthly_rent, status) \
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                    (store_name, category, floor, area, owner_name, owner_phone,
                    owner_email, rent_start, rent_end, monthly_rent, status))
                con.commit()
                flash('Магазин успішно додано')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Помилка при додаванні магазину: {str(e)}')
            return redirect(url_for('addstore'))
    return render_template('addstore.html')

@app.route('/deletestore/<int:id>', methods=['POST'])
def deletestore(id):
    if not session.get('admin'):
        flash('Доступ заборонено. Потрібні права адміністратора.')
        return redirect(url_for('index'))
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM stores WHERE id=?", (id,))
            con.commit()
            flash('Магазин успішно видалено')
    except Exception as e:
        flash(f'Помилка при видаленні магазину: {str(e)}')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
