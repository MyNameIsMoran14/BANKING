from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os

# --- Настройка приложения ---
app = Flask(__name__)
app.secret_key = "supersecret"  # лучше заменить на свой ключ

# --- Настройка базы данных SQLite ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Модель пользователя с ролями ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(20), default='client')  # client, manager, admin
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(150))  # Кто создал аккаунт (для менеджеров)

# --- Создаём таблицы при первом запуске ---
with app.app_context():
    db.create_all()
    
    # Создаем начального админа если его нет
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin',
            password='admin123',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("🔐 Создан начальный админ: admin / admin123")

# --- Маршруты ---
@app.route('/')
def index():
    user = session.get('user', None)
    role = session.get('role', None)
    return render_template('index.html', user=user, role=role)

@app.route('/small_business')
def small_business():
    return render_template('small_business.html')

@app.route('/big_business')
def big_business():
    return render_template('big_business.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if User.query.filter_by(username=username).first():
            flash("❌ Пользователь с таким логином уже существует!")
            return redirect(url_for("register"))

        new_user = User(username=username, password=password, role='client')
        db.session.add(new_user)
        db.session.commit()

        flash("✅ Регистрация успешна!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    
    if user and user.is_active:
        session['user'] = user.username
        session['role'] = user.role
        flash(f"Привет, {user.username}! (Роль: {user.role})", "success")
        print(f"🔐 Вход: {username} с ролью {user.role}")
        
        # Редирект в зависимости от роли
        if user.role == 'admin':
            return redirect(url_for('admin_panel'))
        elif user.role == 'manager':
            return redirect(url_for('manager_panel'))
        else:
            return redirect(url_for('index'))
    else:
        flash("Неверный логин или пароль!", "error")
        return redirect(url_for('index'))

# --- Выход ---
@app.route('/logout')
def logout():
    username = session.get('user')
    session.clear()
    flash(f"Вы вышли из аккаунта!", "info")
    return redirect(url_for('index'))

# --- Админ панель ---
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    
    users = User.query.all()
    return render_template('admin.html', users=users)

# --- Панель менеджера ---
@app.route('/manager')
def manager_panel():
    if session.get('role') != 'manager':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    
    return render_template('manager.html')

# --- Создание менеджера (только админ) ---
@app.route('/admin/create_manager', methods=['POST'])
def create_manager():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    
    username = request.form['username']
    password = request.form['password']
    role = request.form.get('role', 'manager')  # По умолчанию менеджер
    
    if User.query.filter_by(username=username).first():
        flash("Пользователь с таким логином уже существует!", "error")
        return redirect(url_for('admin_panel'))
    
    new_user = User(
        username=username,
        password=password,
        role=role,
        created_by=session['user']
    )
    db.session.add(new_user)
    db.session.commit()
    
    flash(f"Пользователь {username} создан с ролью {role}!", "success")
    return redirect(url_for('admin_panel'))

# --- Блокировка/разблокировка пользователей ---
@app.route('/admin/toggle_user', methods=['POST'])
def toggle_user():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    
    user_id = request.form['user_id']
    user = User.query.get(user_id)
    
    if user and user.role != 'admin':  # Нельзя блокировать админов
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"Пользователь {user.username} {'заблокирован' if not user.is_active else 'активирован'}!", "success")
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/change_role', methods=['POST'])
def change_role():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    
    user_id = request.form['user_id']
    new_role = request.form['new_role']
    user = User.query.get(user_id)
    
    if user:
        # Запрещаем менять роль основному админу admin
        if user.username == 'admin':
            flash("Нельзя изменить роль основного администратора!", "error")
        # Проверяем, не пытаемся ли изменить роль текущего админа
        elif user.username == session.get('user'):
            flash("Нельзя изменить свою собственную роль!", "error")
        else:
            user.role = new_role
            db.session.commit()
            flash(f"Роль пользователя {user.username} изменена на {new_role}!", "success")
    
    return redirect(url_for('admin_panel'))

# --- Запуск ---
if __name__ == "__main__":
    app.run(debug=True)