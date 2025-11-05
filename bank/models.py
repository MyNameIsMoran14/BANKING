from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200))
    role = db.Column(db.String(50), default='client')
    is_active = db.Column(db.Boolean, default=True)
    created_by = db.Column(db.String(150))  # если нужно хранить, кто создал менеджера

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class CreditApplication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(150))
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default="Новая")
    created_at = db.Column(db.DateTime, server_default=db.func.now())
