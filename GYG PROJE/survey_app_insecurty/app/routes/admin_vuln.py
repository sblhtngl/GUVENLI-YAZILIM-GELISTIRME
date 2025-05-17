from flask import Blueprint, render_template

admin_vuln_bp = Blueprint("admin_vuln", __name__)

@admin_vuln_bp.route("/vuln_admin")
def vuln_admin_panel():
    return render_template("admin.html")
