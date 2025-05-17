from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import mysql
import MySQLdb.cursors

vote_bp = Blueprint("vote", __name__, url_prefix="/vote")

@vote_bp.route("/submit", methods=["POST"])
@login_required
def submit_vote():
    survey_id = request.form.get("survey_id")
    answer = request.form.get("answer")

    try:
        survey_id = int(survey_id)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz anket ID'si."}), 400

    if not answer:
        return jsonify({"success": False, "message": "Lütfen bir seçenek seçin."}), 400

    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Daha önce oy verilip verilmediğini kontrol et
    cur.execute("SELECT id FROM answers WHERE survey_id = %s AND user_id = %s", (survey_id, current_user.id))
    if cur.fetchone():
        cur.close()
        return jsonify({"success": False, "message": "Zaten oy verdiniz."}), 400

    try:
        cur.execute(
            "INSERT INTO answers (survey_id, user_id, answer) VALUES (%s, %s, %s)",
            (survey_id, current_user.id, answer)
        )
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        return jsonify({"success": False, "message": "Veritabanı hatası: " + str(e)}), 500

    # Güncel sonuçları getir
    cur.execute(
        "SELECT answer, COUNT(*) AS count FROM answers WHERE survey_id = %s GROUP BY answer",
        (survey_id,)
    )
    rows = cur.fetchall()
    cur.close()

    results = [{"answer": row["answer"], "count": row["count"]} for row in rows]
    return jsonify({"success": True, "results": results}), 200
