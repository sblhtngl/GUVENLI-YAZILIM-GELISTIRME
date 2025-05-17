from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app import mysql, csrf
from app.forms.survey_forms import SurveyForm
import MySQLdb.cursors
import logging

survey_bp = Blueprint("survey", __name__, url_prefix="/survey")

# 🟢 Anket Oluşturma (Sadece owner)
@survey_bp.route("/create", methods=["GET", "POST"])
@login_required
def create():
    if current_user.role != "owner":
        flash("Bu sayfaya erişim izniniz yok.")
        return redirect(url_for("survey.vote_list"))

    form = SurveyForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO surveys (user_id, title, question, option1, option2, option3, option4)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            current_user.id,
            form.title.data.strip(),
            form.question.data.strip(),
            form.option1.data.strip(),
            form.option2.data.strip(),
            form.option3.data.strip(),
            form.option4.data.strip()
        ))
        mysql.connection.commit()
        cur.close()
        flash("Anket başarıyla oluşturuldu.")
        return redirect(url_for("survey.list_surveys"))

    return render_template("create_survey.html", form=form)

# 🟢 Anket Listeleme (Admin ve Owner)
@survey_bp.route("/list", endpoint="list_surveys")
@login_required
def list_surveys():
    if current_user.role not in ["admin", "owner"]:
        flash("Bu sayfaya erişim izniniz yok.")
        return redirect(url_for("survey.vote_list"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT s.id, s.title, s.question, u.username
        FROM surveys s JOIN users u ON s.user_id = u.id
    """)
    surveys = cur.fetchall()
    cur.close()
    return render_template("admin_survey_list.html", surveys=surveys)

# 🟢 Oy Verme ve Sonuç Gösterimi
@survey_bp.route("/answer/<int:survey_id>", methods=["GET", "POST"])
@login_required
def answer(survey_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id FROM answers WHERE survey_id = %s AND user_id = %s", (survey_id, current_user.id))
    already_voted = cur.fetchone()

    if request.method == "POST":
        if already_voted:
            cur.close()
            return jsonify({"success": False, "message": "Bu ankete zaten oy verdiniz."})

        answer = request.form.get("answer")
        if not answer:
            cur.close()
            return jsonify({"success": False, "message": "Lütfen bir seçenek seçin."})

        cur.execute("INSERT INTO answers (survey_id, user_id, answer) VALUES (%s, %s, %s)",
                    (survey_id, current_user.id, answer))
        mysql.connection.commit()
        cur.close()
        return jsonify({"success": True})

    cur.execute("SELECT title, question, option1, option2, option3, option4 FROM surveys WHERE id = %s", (survey_id,))
    survey = cur.fetchone()
    cur.execute("SELECT answer, COUNT(*) as total FROM answers WHERE survey_id = %s GROUP BY answer", (survey_id,))
    results = cur.fetchall()
    total = sum([r["total"] for r in results]) if results else 0
    cur.close()

    return render_template("answer_survey.html", survey=survey, results=results, total=total,
                           survey_id=survey_id, already_voted=already_voted)

# 🟢 Anket Güncelleme (Sadece owner)
@survey_bp.route("/update/<int:id>", methods=["GET", "POST"])
@login_required
def update_survey(id):
    if current_user.role != "owner":
        flash("Bu sayfaya erişim izniniz yok.")
        return redirect(url_for("survey.vote_list"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM surveys WHERE id = %s", (id,))
    survey = cur.fetchone()

    if not survey:
        cur.close()
        return "Anket bulunamadı.", 404

    form = SurveyForm(data=survey)
    if form.validate_on_submit():
        cur.execute("""
            UPDATE surveys SET title = %s, question = %s, option1 = %s, option2 = %s, option3 = %s, option4 = %s
            WHERE id = %s
        """, (
            form.title.data.strip(), form.question.data.strip(),
            form.option1.data.strip(), form.option2.data.strip(),
            form.option3.data.strip(), form.option4.data.strip(), id
        ))
        mysql.connection.commit()
        cur.close()
        flash("Anket güncellendi.")
        return redirect(url_for("survey.list_surveys"))

    cur.close()
    return render_template("update_survey.html", form=form)

# 🟢 Anket Silme (Sadece owner)
@survey_bp.route("/delete/<int:id>")
@login_required
def delete_survey(id):
    if current_user.role != "owner":
        flash("Bu sayfaya erişim izniniz yok.")
        return redirect(url_for("survey.vote_list"))

    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM answers WHERE survey_id = %s", (id,))
        cur.execute("DELETE FROM surveys WHERE id = %s", (id,))
        mysql.connection.commit()
        flash("Anket silindi.")
    except Exception as e:
        mysql.connection.rollback()
        logging.error(f"Anket silme hatası: {e}")
        flash("Silme işlemi başarısız.")
    finally:
        cur.close()
    return redirect(url_for("survey.list_surveys"))

# 🟢 Oylanabilir Anketler (Sadece user)
@survey_bp.route("/vote", endpoint="vote_list")
@login_required
def vote_list():
    if current_user.role != "user":
        flash("Bu sayfaya yalnızca kullanıcılar erişebilir.")
        return redirect(url_for("survey.list_surveys"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, title, question FROM surveys")
    surveys = cur.fetchall()
    cur.close()
    return render_template("vote_list.html", surveys=surveys)

# 🟢 Sonuçlar (Sadece admin)
@survey_bp.route("/results")
@login_required
def results():
    if current_user.role != "admin":
        flash("Bu sayfa sadece adminler içindir.")
        return redirect(url_for("survey.vote_list"))

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT s.title, s.question, a.answer, COUNT(*) as count 
        FROM answers a JOIN surveys s ON s.id = a.survey_id
        GROUP BY s.title, s.question, a.answer ORDER BY s.title
    """)
    results = cur.fetchall()
    cur.close()
    return render_template("admin_survey_list.html", results=results)

# 🔓 Zafiyetli Versiyonlar (rol kontrolü yok)
@survey_bp.route("/list_vuln", endpoint="list_surveys_vuln")
def list_surveys_vuln():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT s.id, s.title, s.question, u.username FROM surveys s JOIN users u ON s.user_id = u.id")
    surveys = cur.fetchall()
    cur.close()
    return render_template("admin_survey_list.html", surveys=surveys)

@survey_bp.route("/vote_vuln", endpoint="vote_list_vuln")
def vote_list_vuln():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id, title, question FROM surveys")
    surveys = cur.fetchall()
    cur.close()
    return render_template("vote_list.html", surveys=surveys)

@survey_bp.route("/results_vuln", endpoint="results_vuln")
def results_vuln():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT s.title, s.question, a.answer, COUNT(*) as count 
        FROM answers a JOIN surveys s ON s.id = a.survey_id
        GROUP BY s.title, s.question, a.answer ORDER BY s.title
    """)
    results = cur.fetchall()
    cur.close()
    return render_template("admin_survey_list.html", results=results)

# 🔓 CSRF Korumalı olmayan (Zafiyetli) oy gönderme endpoint'i
@csrf.exempt
@survey_bp.route("/vote/submit", methods=["POST"])
@login_required
def vote_submit():
    survey_id = request.form.get("survey_id")
    answer = request.form.get("answer")

    if not survey_id or not answer:
        return jsonify({"success": False, "message": "Geçersiz veri."})

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT id FROM answers WHERE survey_id = %s AND user_id = %s", (survey_id, current_user.id))
    already_voted = cur.fetchone()

    if already_voted:
        cur.close()
        return jsonify({"success": False, "message": "Zaten oy verdiniz."})

    try:
        cur.execute("INSERT INTO answers (survey_id, user_id, answer) VALUES (%s, %s, %s)",
                    (survey_id, current_user.id, answer))
        mysql.connection.commit()
        return jsonify({"success": True})
    except Exception as e:
        mysql.connection.rollback()
        logging.error(f"Vote submit error: {e}")
        return jsonify({"success": False, "message": "Veritabanı hatası."})
    finally:
        cur.close()
