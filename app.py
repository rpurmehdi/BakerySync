import os
from flask import Flask, flash, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from models import db, Source, Destination, IngredientType, ProductionType, IngredientArrival, Recipe, Production, production_arrival_association, ProductionShipment, recipe_ingredient_association
from routes.types import types_bp
from routes.sources import sources_bp
from routes.destinations import destinations_bp
from routes.arrivals import arrivals_bp
from routes.shipments import shipments_bp
from routes.productions import productions_bp
from routes.recipes import recipes_bp
app = Flask(__name__)

path = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(path, 'bakerysync.db')

app.secret_key = 'very_secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()


def create_tables():
    db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.template_filter('escape_html')
def escape_html_filter(s):
    result = ""
    for c in s:
        if c in ["'", "<", ">", "&", '"']:
            result += "."
        else:
            result += c
    return result


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template(
            "index.html"
        )
    else:
        return render_template("index.html")


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
