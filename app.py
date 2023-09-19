import os
from flask import Flask, flash, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


app = Flask(__name__)

path = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(path, 'bakerysync.db')

db = SQLAlchemy(app)

#Python classes for all tables
class Source(db.Model):
    __tablename__ = 'Sources'

    source_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    source_name = db.Column(db.String, nullable=False, unique=True)
    source_contact_person = db.Column(db.String)
    contact_information = db.Column(db.String)
    source_type = db.Column(db.String, nullable=False)
    source_location = db.Column(db.String)
    source_description = db.Column(db.String)

class Destination(db.Model):
    __tablename__ = 'Destinations'

    destination_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    destination_name = db.Column(db.String, nullable=False, unique=True)
    destination_contact_person = db.Column(db.String)
    contact_information = db.Column(db.String)
    destination_type = db.Column(db.String)
    destination_location = db.Column(db.String)
    destination_description = db.Column(db.String)

class RawMaterialType(db.Model):
    __tablename__ = 'RawMaterialTypes'

    material_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_name = db.Column(db.String, nullable=False, unique=True)

class ProductionType(db.Model):
    __tablename__ = 'ProductionTypes'

    production_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    production_name = db.Column(db.String, nullable=False, unique=True)

class RawMaterialArrival(db.Model):
    __tablename__ = 'RawMaterialArrival'

    arrival_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    material_id = db.Column(db.Integer, db.ForeignKey('RawMaterialTypes.material_id'), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    source_id = db.Column(db.Integer, db.ForeignKey('Sources.source_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    material = db.relationship('RawMaterialType', backref='arrivals')
    source = db.relationship('Source', backref='arrivals')

class RawMaterialUsage(db.Model):
    __tablename__ = 'RawMaterialUsage'
    
    usage_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    arrival_id = db.Column(db.Integer, db.ForeignKey('raw_material_arrival.arrival_id'), nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('raw_material_type.material_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    batch_id = db.Column(db.Integer, nullable=False)

    material = db.relationship('RawMaterialType', backref='usage')
    arrival = db.relationship('RawMaterialArrival', backref='usage')

class Recipe(db.Model):
    __tablename__ = 'Recipes'
    
    recipe_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_name = db.Column(db.String, nullable=False, unique=True)
    recipe_description = db.Column(db.Text)

class RecipeRawMaterialtype(db.Model):
    __tablename__ = 'RecipeRawMaterialtypes'

    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.recipe_id'), primary_key=True, nullable=False)
    material_id = db.Column(db.Integer, db.ForeignKey('rawmaterialtypes.material_id'), primary_key=True, nullable=False)
    quantity_percent = db.Column(db.Float, nullable=False)

    recipe = db.relationship('Recipes', backref=db.backref('recipe_raw_materialtypes', cascade='all, delete-orphan'))
    material = db.relationship('RawMaterialTypes', backref=db.backref('recipe_raw_materialtypes', cascade='all, delete-orphan'))

    __table_args__ = (
        db.UniqueConstraint('recipe_id', 'material_id', name='_recipe_material_uc'),
    )

class Production(db.Model):
    __tablename__ = 'productions'

    batch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    print_batch = db.Column(db.String, nullable=False, unique=True)
    production_id = db.Column(db.Integer, nullable=False)
    production_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    recipe_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    product = db.relationship('ProductionType', backref='productions')
    recipe = db.relationship('Recipe', backref='productions')

class ProductionRawMaterialArrival(db.Model):
    __tablename__ = 'productionrawmaterialarrivals'

    batch_id = db.Column(db.Integer, nullable=False)
    arrival_id = db.Column(db.Integer, nullable=False)

    production = db.relationship('Production', backref='raw_material_arrivals')
    raw_material_arrival = db.relationship('RawMaterialArrival', backref='productions')

    __table_args__ = (
        db.ForeignKeyConstraint(['batch_id'], ['production.batch_id']),
        db.ForeignKeyConstraint(['arrival_id'], ['rawmaterialarrival.arrival_id'])
    )

class ProductionShipping(db.Model):
    __tablename__ = 'productionshipping'

    shipping_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('production.batch_id'), nullable=False)
    production_id = db.Column(db.Integer, db.ForeignKey('productiontypes.production_id'), nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey('destinations.destination_id'), nullable=False)
    shipping_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    production = db.relationship('Production', backref='shipping')
    production_type = db.relationship('ProductionTypes', backref='shipping')
    destination = db.relationship('Destinations', backref='shipping')

class InStockRawMaterials(db.Model):
    __tablename__ = 'instockrawmaterials'

    arrival_id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.Integer, db.ForeignKey('rawmaterialtypes.material_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    raw_material = db.relationship('RawMaterialTypes', backref='in_stock')

class InStockProducts(db.Model):
    __tablename__ = 'instockproducts'

    batch_id = db.Column(db.Integer, primary_key=True)
    production_id = db.Column(db.Integer, db.ForeignKey('production.batch_id'), nullable=False)
    quantity = db.Column(db.Float, nullable=False)

    production = db.relationship('Production', backref='in_stock_products')
    production_type = db.relationship('ProductionTypes', backref='in_stock_products')

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET", "POST"])

def index():
    if request.method == "POST":
        return render_template(
            "index.html"
        )
    else:
        return render_template("index.html")

'''
EXAMPLE OF USING THE db FUNCTION FOR SQL QUERY:
# Example for SELECT


# Example for INSERT


# Example for DELETE


# Example for UPDATE
'''
