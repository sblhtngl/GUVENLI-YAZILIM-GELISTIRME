from flask import Blueprint, render_template, redirect, url_for, flash, session
from flask_login import login_user, logout_user
from app import mysql, login_manager
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm  # ✅ doğru yerden import
import bcrypt
import MySQLdb.cursors

auth_bp = Blueprint("auth", __name__)

# Kullanıcı oturumunu yükle
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user["id"], username=user["username"], role=user["role"])
    return None

# 🔐 Giriş
@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute("SELECT id, username, password, role FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        if user and bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
            user_obj = User(id=user["id"], username=user["username"], role=user["role"])
            login_user(user_obj)
            return redirect(url_for("dashboard.home"))
        else:
            flash("Geçersiz kullanıcı adı veya şifre.")

    return render_template("login.html", form=form)

# 🧾 Kayıt
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        role = form.role.data

        hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        cur = mysql.connection.cursor()
        try:
            cur.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                        (username, hashed_pw, role))
            mysql.connection.commit()
            flash("Kayıt başarılı! Giriş yapabilirsiniz.")
            return redirect(url_for("auth.login"))
        except Exception as e:
            flash("Bu kullanıcı adı zaten kayıtlı.")
            print("Kayıt hatası:", str(e))
            return redirect(url_for("auth.register"))
        finally:
            cur.close()

    return render_template("register.html", form=form)

# 🚪 Çıkış
@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))
