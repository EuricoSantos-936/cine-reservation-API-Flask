from flask import Flask
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from api.models.models import User
from api.views.views import main_view
from api.orm import data_orm
from flask_migrate import Migrate
from flasgger import Swagger

def create_app():
    """
    Initializes the Flask app and all its components.

    Returns:
        Flask: The initialized app
    """
    app = Flask(__name__)
    app.register_blueprint(main_view, url_prefix="")
    app.config.from_pyfile('config.py')
    data_orm.init_app(app)
    
    Migrate(app, data_orm.db)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"

    JWTManager(app)

    swagger_config = {
        "swagger": "2.0",
        "info": {
            "title": "Cine Reservation API",
            "description": "API for managing movie reservations",
            "version": "1.0.0"
        },
        "specs": [
            {
                "endpoint": 'apispec_1',
                "route": '/apispec_1.json',
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/flasgger_static",
        "swagger_ui": True,
        "specs_route": "/apidocs/",
        "headers": [
        ],
    }
    Swagger(app, config=swagger_config)
    
    @login_manager.user_loader
    def load_user(user_id):
        """
        Loads a user from the database by their user ID.

        This function is used by Flask-Login to retrieve a user object
        from the database based on the user ID stored in the session.
        
        Args:
            user_id (str): The ID of the user to load.

        Returns:
            User: The user object if found, otherwise None.
         """
        return User.query.get(int(user_id)) 
    
    def create_default_admin():
        """
        Creates a default admin user if none exists in the database.

        The default admin has the username "admin" and password "admin".

        This function is used when the database is first created to ensure
        that there is an admin user account available for use.

        """
        default_admin = User(username="admin")
        default_admin.set_password("admin")
        default_admin.is_admin = True
        data_orm.db.session.add(default_admin)
        data_orm.db.session.commit()

    with app.app_context():
        data_orm.db.create_all()
        if not User.query.filter_by(is_admin=True).first():
            create_default_admin()

    return app
