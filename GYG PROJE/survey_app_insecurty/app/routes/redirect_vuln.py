from flask import Blueprint, request, redirect

# 🔴 Open Redirect zafiyeti taşıyan blueprint

redirect_vuln_bp = Blueprint("redirect_vuln", __name__)

@redirect_vuln_bp.route("/vuln_redirect")
def vuln_redirect():
    url = request.args.get("url")
    return redirect(url)
