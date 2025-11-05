from flask import Flask, render_template, request, redirect, url_for, flash, session
from models import db, User, CreditApplication
from tasks import process_credit_application
import os

app = Flask(__name__)
app.secret_key = "supersecret"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()  

    # Создание админа
    if not User.query.filter_by(role='admin').first():
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("🔐 Создан начальный админ: admin / admin123")


# --- Маршруты ---
@app.route('/')
def index():
    return render_template('index.html', user=session.get('user'), role=session.get('role'))

@app.route('/small_business')
def small_business():
    return render_template('small_business.html')

@app.route('/big_business')
def big_business():
    return render_template('big_business.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/user_agreement')
def user_agreement():
    return render_template('user_agreement.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')


# --- Регистрация и логин ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким логином уже существует!", "error")
            return redirect(url_for("register"))

        new_user = User(username=username, role='client')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash("Регистрация успешна!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    user = User.query.filter_by(username=username).first()
    if user and user.is_active and user.check_password(password):
        session['user'] = user.username
        session['role'] = user.role
        flash(f"Привет, {user.username}! (Роль: {user.role})", "success")

        if user.role == 'admin':
            return redirect(url_for('admin_panel'))
        elif user.role == 'manager':
            return redirect(url_for('manager_panel'))
        return redirect(url_for('index'))
    flash("Неверный логин или пароль!", "error")
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.clear()
    flash("Вы вышли из аккаунта!", "info")
    return redirect(url_for('index'))


# --- Админка ---
@app.route('/admin')
def admin_panel():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    users = User.query.all()
    return render_template('admin.html', users=users)


@app.route('/admin/create_manager', methods=['POST'])
def create_manager():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    username = request.form['username'].strip()
    password = request.form['password'].strip()
    role = request.form.get('role', 'manager')
    if User.query.filter_by(username=username).first():
        flash("Пользователь с таким логином уже существует!", "error")
        return redirect(url_for('admin_panel'))

    new_user = User(username=username, role=role, created_by=session['user'])
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()
    flash(f"Пользователь {username} создан с ролью {role}!", "success")
    return redirect(url_for('admin_panel'))


@app.route('/admin/toggle_user', methods=['POST'])
def toggle_user():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    user = User.query.get(request.form['user_id'])
    if user and user.role != 'admin':
        user.is_active = not user.is_active
        db.session.commit()
        flash(f"Пользователь {user.username} {'заблокирован' if not user.is_active else 'активирован'}!", "success")
    return redirect(url_for('admin_panel'))


@app.route('/admin/delete_user', methods=['POST'])
def delete_user():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    user = User.query.get(request.form['user_id'])
    if user and user.username != 'admin' and user.username != session.get('user'):
        db.session.delete(user)
        db.session.commit()
        flash(f"Пользователь {user.username} удален!", "success")
    return redirect(url_for('admin_panel'))


@app.route('/admin/change_role', methods=['POST'])
def change_role():
    if session.get('role') != 'admin':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    user = User.query.get(request.form['user_id'])
    new_role = request.form.get('new_role')
    if user and user.username != 'admin' and user.username != session.get('user'):
        user.role = new_role
        db.session.commit()
        flash(f"Роль пользователя {user.username} изменена на {new_role}!", "success")
    return redirect(url_for('admin_panel'))


# --- Менеджер ---
@app.route('/manager')
def manager_panel():
    if session.get('role') != 'manager':
        flash("Доступ запрещен!", "error")
        return redirect(url_for('index'))
    applications = CreditApplication.query.order_by(CreditApplication.id.desc()).all()
    return render_template('manager.html', applications=applications)


# --- Подать заявку ---
@app.route('/submit_credit_form', methods=['POST'])
def submit_credit_form():
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    amount = request.form.get('amount', '').strip()

    if not name or not phone or not amount:
        flash("Пожалуйста, заполните все обязательные поля!", "error")
        return redirect(url_for('index'))

    try:
        amount_val = float(amount)
        if amount_val <= 0:
            flash("Сумма кредита должна быть больше нуля!", "error")
            return redirect(url_for('index'))
    except ValueError:
        flash("Некорректная сумма кредита!", "error")
        return redirect(url_for('index'))

    user = None
    if 'user' in session:
        user = User.query.filter_by(username=session['user']).first()

    application = CreditApplication(
        name=name,
        phone=phone,
        email=email,
        amount=amount_val,
        user_id=user.id if user else None
    )

    db.session.add(application)  # сохраняем в той же базе
    db.session.commit()

    process_credit_application(application.id)
    flash("Ваша заявка принята! Мы рассмотрим её в ближайшее время.", "success")
    return redirect(url_for('index'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
