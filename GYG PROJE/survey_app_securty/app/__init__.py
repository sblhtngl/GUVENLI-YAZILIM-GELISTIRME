import os
import logging
from datetime import timedelta
from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from dotenv import load_dotenv

# ✅ .env dosyasını yükle (SECRET_KEY gibi değerler için)
load_dotenv()

# ✅ Uzantı başlatıcıları
mysql = MySQL()
login_manager = LoginManager()
csrf = CSRFProtect()

# ✅ Giriş sayfasına yönlendirme ayarı
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"  # flash mesaj kategorisi (opsiyonel)

def create_app():
    app = Flask(__name__)

    # 🔐 Güvenli anahtar (CSRF, oturum vb. için zorunlu)
    app.secret_key = os.environ.get("SECRET_KEY", "gizli_anahtar")

    # ⏱ Oturum zaman aşımı (isteğe bağlı güvenlik için)
    app.permanent_session_lifetime = timedelta(minutes=30)

    # 🔌 MySQL yapılandırması (.env'den veya varsayılanlardan alır)
    app.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST", "localhost")
    app.config["MYSQL_USER"] = os.environ.get("MYSQL_USER", "root")
    app.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD", "131658")
    app.config["MYSQL_DB"] = os.environ.get("MYSQL_DB", "survey_app")
    app.config["MYSQL_CURSORCLASS"] = "DictCursor"

    # ⚙️ Uzantıların Flask uygulamasına bağlanması
    mysql.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # 🔗 Blueprint'lerin kayıt edilmesi
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.survey import survey_bp
    from app.routes.admin_manage import admin_manage_bp
    from app.routes.vote import vote_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(survey_bp)
    app.register_blueprint(admin_manage_bp)
    app.register_blueprint(vote_bp)

    # 📝 Loglama (gerektiğinde konsola bilgi basar)
    logging.basicConfig(level=logging.INFO)
    app.logger.info("Uygulama başarıyla başlatıldı.")

    return app
