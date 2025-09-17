from .login import login_bp
from .details_modify import detail_register_bp
from .bot_routes import bot_bp
from .chats import chat_logger_bp
from .flashai import flashai_bp
from .current_affair import current_bp
def register_routes(app):
    app.register_blueprint(login_bp)
    app.register_blueprint(detail_register_bp)
    app.register_blueprint(bot_bp)
    app.register_blueprint(chat_logger_bp)
    app.register_blueprint(flashai_bp)
    app.register_blueprint(current_bp)
