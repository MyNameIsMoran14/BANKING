from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import os

# --- Настройка приложения ---
app = Flask(__name__)
app.secret_key = "supersecret"  # лучше заменить на свой ключ

# --- Настройка базы данных SQLite ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Модель пользователя ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# --- Создаём таблицы при первом запуске ---
with app.app_context():
    db.create_all()

# --- Маршруты ---
@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

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

        # Проверка на существующего пользователя
        if User.query.filter_by(username=username).first():
            flash("❌ Пользователь с таким логином уже существует!")
            return redirect(url_for("register"))  # останемся на странице регистрации

        # Добавление пользователя в БД
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        # УСПЕШНАЯ регистрация → без flash
        from flask import session
        session['open_login_modal'] = True  # сразу открываем модалку входа
        return redirect(url_for("index"))

    return render_template("register.html")

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        # сохраняем пользователя в сессию
        from flask import session
        session['user'] = user.username
        flash(f"Привет, {user.username}!")
    else:
        flash("Неверный логин или пароль!")
    return redirect(url_for('index'))

# --- Выход ---
@app.route('/logout')
def logout():
    from flask import session
    session.pop('user', None)
    flash("Вы вышли из аккаунта")
    return redirect(url_for('index'))

# --- Запуск ---
if __name__ == "__main__":
    app.run(debug=True)