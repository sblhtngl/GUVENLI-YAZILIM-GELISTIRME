from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import mysql
import MySQLdb.cursors  # DictCursor için

admin_manage_bp = Blueprint("admin_manage", __name__, url_prefix="/admin/surveys")


# ADMIN tüm anketleri listeleyebilir
# OWNER sadece kendi anketlerini görür
@admin_manage_bp.route("/", endpoint="list_surveys")
@login_required
def list_surveys():
    if current_user.role not in ["admin", "owner"]:
        flash("Yetkisiz erişim.")
        return redirect(url_for("dashboard.home"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if current_user.role == "admin":
        cur.execute("""
            SELECT s.id, s.title, s.question, s.user_id, u.username
            FROM surveys s JOIN users u ON s.user_id = u.id
        """)
    else:
        cur.execute("""
            SELECT s.id, s.title, s.question, s.user_id, u.username
            FROM surveys s JOIN users u ON s.user_id = u.id
            WHERE s.user_id = %s
        """, (current_user.id,))
    surveys = cur.fetchall()
    return render_template("admin_survey_list.html", surveys=surveys)


# SADECE OWNER güncelleyebilir ve sadece kendi anketini
@admin_manage_bp.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_survey(id):
    if current_user.role != "owner":
        flash("Yetkisiz erişim.")
        return redirect(url_for("dashboard.home"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM surveys WHERE id = %s", (id,))
    survey = cur.fetchone()

    if not survey or survey["user_id"] != current_user.id:
        flash("Yalnızca kendi anketinizi güncelleyebilirsiniz.")
        return redirect(url_for("admin_manage.list_surveys"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        question = request.form.get("question", "").strip()

        if not title or not question:
            flash("Başlık ve soru boş olamaz.")
            return redirect(url_for("admin_manage.update_survey", id=id))

        cur.execute("UPDATE surveys SET title = %s, question = %s WHERE id = %s", (title, question, id))
        mysql.connection.commit()
        flash("Anket başarıyla güncellendi.")
        return redirect(url_for("admin_manage.list_surveys"))

    return render_template("update_survey.html", survey=survey)


# SADECE OWNER silebilir ve sadece kendi anketini
@admin_manage_bp.route("/delete/<int:id>")
@login_required
def delete_survey(id):
    if current_user.role != "owner":
        flash("Yetkisiz erişim.")
        return redirect(url_for("dashboard.home"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT user_id FROM surveys WHERE id = %s", (id,))
    survey = cur.fetchone()

    if not survey or survey["user_id"] != current_user.id:
        flash("Yalnızca kendi anketinizi silebilirsiniz.")
        return redirect(url_for("admin_manage.list_surveys"))

    cur.execute("DELETE FROM surveys WHERE id = %s", (id,))
    mysql.connection.commit()
    flash("Anket başarıyla silindi.")
    return redirect(url_for("admin_manage.list_surveys"))
