from flask import Flask
from flask_cors import CORS
from utils.routes import routes_blueprint
from utils.auth_routes import auth_blueprint

app = Flask(__name__)
CORS(app)

app.register_blueprint(routes_blueprint)
app.register_blueprint(auth_blueprint)

if __name__ == "__main__":
    app.run(debug=True)

# gunicorn -c gunicorn_config.py app:app