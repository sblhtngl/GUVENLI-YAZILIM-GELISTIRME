from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user
from app import mysql, login_manager
from app.models.user import User
from app.forms.auth_forms import LoginForm, RegisterForm
import bcrypt
import MySQLdb.cursors

# 🔴 Zafiyetli blueprint tanımı
auth_bp = Blueprint("auth_vuln", __name__)

# 🔓 Logout
@auth_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("auth_vuln.vuln_login"))

# 🧠 Kullanıcı oturumunu yükle (Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    if user:
        return User(id=user["id"], username=user["username"], role=user["role"])
    return None

# 🔓 SQL Injection açık login
@auth_bp.route("/login", methods=["GET", "POST"])
def vuln_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # 🔓 SQL Injection'a açık sorgu (tek tırnak kapanma hatasına karşı)
        if "--" in username:
            query = f"SELECT id, username, password, role FROM users WHERE username = '{username}"
        else:
            query = f"SELECT id, username, password, role FROM users WHERE username = '{username}'"

        print("[SQL DEBUG]", query)  # test için terminale yaz

        try:
            cur.execute(query)
            user = cur.fetchone()
        except Exception as e:
            flash("SQL sorgusu çalıştırılamadı.")
            user = None

        cur.close()

        # Şifre kontrolü kaldırıldı — sadece kullanıcı varsa giriş yapılır
        if user:
            user_obj = User(id=user["id"], username=user["username"], role=user["role"])
            login_user(user_obj)
            return redirect(url_for("dashboard.home"))
        else:
            flash("Geçersiz kullanıcı adı veya şifre.")

    return render_template("login.html", form=form)

# 🔓 SQL Injection açık kayıt (register)
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
            # 🔥 SQL Injection zafiyeti (f-string ile sorgu)
            query = f"INSERT INTO users (username, password, role) VALUES ('{username}', '{hashed_pw}', '{role}')"
            print("[SQL DEBUG]", query)
            cur.execute(query)
            mysql.connection.commit()
            flash("Kayıt başarılı. Giriş yapabilirsiniz.")
            return redirect(url_for("auth_vuln.vuln_login"))
        except Exception as e:
            flash("Kullanıcı adı zaten kayıtlı olabilir.")
        finally:
            cur.close()

    return render_template("register.html", form=form)
