from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/")
@login_required
def home():
    if current_user.role == "user":
        flash("Yalnızca oylama işlemleri yapabilirsiniz.")
        return redirect(url_for("survey.vote_list"))

    if current_user.role in ["admin", "owner"]:
        return render_template("dashboard.html")

    flash("Bu sayfaya erişim yetkiniz yok.")
    return redirect(url_for("auth.login"))
