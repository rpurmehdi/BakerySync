import os
from flask import Flask
from models import db
from routes.index import index_bp
from routes.types import types_bp
from routes.sources import sources_bp
from routes.destinations import destinations_bp
from routes.arrivals import arrivals_bp
from routes.shipments import shipments_bp
from routes.productions import productions_bp
from routes.recipes import recipes_bp
app = Flask(__name__)

# path to database file
path = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(path, 'bakerysync.db')

# secret key
app.secret_key = 'very_secret_key'

# initiate the app
db.init_app(app)

# create database and tables if not created
with app.app_context():
    db.create_all()

# set HTTP response headers that prevent caching


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# escape HTML entities for java script


@app.template_filter('escape_html')
def escape_html_filter(s):
    result = ""
    for c in s:
        if c in ["'", '"']:
            result += "\\" + c
        else:
            result += c
    return result

# sort ingredients based on recipe.getp


@app.template_filter('sortgetp')
def sortgetp(ingredients, recipe):
    return sorted(ingredients, key=lambda x: recipe.getp(x.id))

# sort ingredients based on production.getu


@app.template_filter('sortgetu')
def sortgetu(ingredients, production):
    return sorted(ingredients, key=lambda x: production.getu(x.id))


# registering index.py
app.register_blueprint(index_bp)

# registering types.py
app.register_blueprint(types_bp)

# registering sources.py
app.register_blueprint(sources_bp)

# registering destinations.py
app.register_blueprint(destinations_bp)

# registering arrivals.py
app.register_blueprint(arrivals_bp)

# registering shipments.py
app.register_blueprint(shipments_bp)

# registering productions.py
app.register_blueprint(productions_bp)

# registering recipes.py
app.register_blueprint(recipes_bp)

if __name__ == '__main__':
    app.run(debug=True)
