from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Bsae Models


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

# classes for all tables


class Source(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)
    contact_person = db.Column(db.String(255))
    contact_information = db.Column(db.String(255))
    type = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    description = db.Column(db.String(255))

    arrivals = db.relationship('RawMaterialArrival', backref='source')


class Destination(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)
    contact_person = db.Column(db.String(255))
    contact_information = db.Column(db.String(255))
    type = db.Column(db.String(255))
    location = db.Column(db.String(255))
    description = db.Column(db.String(255))

    shippings = db.relationship('ProductionShipping', backref='destination')


recipe_rawmaterial_association = db.Table(
    'recipe_rawmaterial_association',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('material_type', db.Integer,
              db.ForeignKey('raw_material_type.id')),
    db.Column('quantity_percent', db.Float)
)


class RawMaterialType(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)

    arrivals = db.relationship('RawMaterialArrival', backref='type')
    recipes = db.relationship(
        'Recipe', secondary=recipe_rawmaterial_association, back_populates='materials')


class ProductionType(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)

    productions = db.relationship('Production', backref='type')
    recipes = db.relationship('Recipe', backref='product')


class RawMaterialArrival(BaseModel):
    type = db.Column(db.Integer, db.ForeignKey(
        RawMaterialType.id), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Source.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    usages = db.relationship('RawMaterialUsage', backref='arrival')


class Recipe(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255))
    production_type = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)

    materials = db.relationship(
        'RawMaterialType',
        secondary=recipe_rawmaterial_association,
        back_populates='recipes'
    )
    productions = db.relationship('Production', backref='recipe')


class Production(BaseModel):
    print_batch = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)
    production_time = db.Column(db.DateTime, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    material_usages = db.relationship('RawMaterialUsage', backref='production')
    shippings = db.relationship('ProductionShipping', backref='production')


class RawMaterialUsage(BaseModel):
    arrival_id = db.Column(db.Integer, db.ForeignKey(
        RawMaterialArrival.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)


class ProductionShipping(BaseModel):
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)
    destination_id = db.Column(
        db.Integer, db.ForeignKey(Destination.id), nullable=False)
    shipping_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
