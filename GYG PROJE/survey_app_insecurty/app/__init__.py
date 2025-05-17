import os
import logging
from datetime import timedelta
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# Uzantılar (global erişim için dışa açık)
mysql = MySQL()
login_manager = LoginManager()
csrf = CSRFProtect()  # CSRF nesnesi burada oluşturuluyor

# 🔐 Giriş yapılmadığında yönlendirilecek sayfa
login_manager.login_view = "auth_vuln.vuln_login"
login_manager.login_message_category = "info"

def create_app():
    app = Flask(__name__)

    # ✅ Güvenlik ayarları
    app.secret_key = os.environ.get("SECRET_KEY", "gizli_anahtar")
    app.permanent_session_lifetime = timedelta(minutes=30)

    # ✅ MySQL bağlantı ayarları
    app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
    app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
    app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "131658")
    app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "survey_app")
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"

    # ✅ Uzantıları bağla
    mysql.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)  # 🔒 CSRF middleware aktif

    # 🔵 Güvenli modüller
    from app.routes.dashboard import dashboard_bp
    from app.routes.survey import survey_bp
    from app.routes.admin_manage import admin_manage_bp
    from app.routes.vote import vote_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(admin_manage_bp)
    app.register_blueprint(vote_bp)

    # 🔴 Zafiyetli modüller (OWASP testleri için)
    from app.routes.auth_vuln import auth_bp as auth_vuln_bp
    from app.routes.admin_vuln import admin_vuln_bp
    from app.routes.redirect_vuln import redirect_vuln_bp

    app.register_blueprint(auth_vuln_bp)
    app.register_blueprint(admin_vuln_bp)
    app.register_blueprint(redirect_vuln_bp)

    # 📝 Loglama
    logging.basicConfig(level=logging.INFO)
    app.logger.info("🚨 Zafiyetli uygulama başlatıldı.")

    return app
