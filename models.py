from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Bsae Models


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


class StockModel(db.Model):
    __abstract__ = True

# classes for all tables


class Source(BaseModel):
    source_name = db.Column(db.String(255), unique=True, nullable=False)
    source_contact_person = db.Column(db.String(255))
    contact_information = db.Column(db.String(255))
    source_type = db.Column(db.String(255), nullable=False)
    source_location = db.Column(db.String(255))
    source_description = db.Column(db.String(255))

    raw_material_arrivals = db.relationship(
        'RawMaterialArrival', backref='source')


class Destination(BaseModel):
    destination_name = db.Column(db.String(255), unique=True, nullable=False)
    destination_contact_person = db.Column(db.String(255))
    contact_information = db.Column(db.String(255))
    destination_type = db.Column(db.String(255))
    destination_location = db.Column(db.String(255))
    destination_description = db.Column(db.String(255))

    production_shippings = db.relationship(
        'ProductionShipping', backref='destination')


class RawMaterialType(BaseModel):
    material_name = db.Column(db.String(255), unique=True, nullable=False)

    raw_material_arrivals = db.relationship(
        'RawMaterialArrival', backref='material')
    recipe_raw_material_types = db.relationship(
        'RecipeRawMaterialType', backref='material')


class ProductionType(BaseModel):
    production_name = db.Column(db.String(255), unique=True, nullable=False)

    productions = db.relationship('Production', backref='production_type')
    production_shippings = db.relationship(
        'ProductionShipping', backref='production_type_rel')


class RawMaterialArrival(BaseModel):
    material_type = db.Column(db.Integer, db.ForeignKey(
        RawMaterialType.id), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Source.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    raw_material_usages = db.relationship(
        'RawMaterialUsage', backref='raw_material_arrival')


class Recipe(BaseModel):
    recipe_name = db.Column(db.String(255), unique=True, nullable=False)
    recipe_description = db.Column(db.String(255))

    recipe_raw_material_types = db.relationship(
        'RecipeRawMaterialType', backref='recipe')
    productions = db.relationship('Production', backref='recipe')


class RecipeRawMaterialType(BaseModel):
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    material_type = db.Column(db.Integer, db.ForeignKey(
        RawMaterialType.id), nullable=False)
    quantity_percent = db.Column(db.Float, nullable=False)


class Production(BaseModel):
    print_batch = db.Column(db.String(255), unique=True, nullable=False)
    production_type = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)
    production_time = db.Column(db.DateTime, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    raw_material_usages = db.relationship(
        'RawMaterialUsage', backref='production')
    production_raw_material_arrivals = db.relationship(
        'ProductionRawMaterialArrival', backref='production')
    production_shippings = db.relationship(
        'ProductionShipping', backref='production',
    )


class RawMaterialUsage(BaseModel):
    arrival_id = db.Column(db.Integer, db.ForeignKey(
        RawMaterialArrival.id), nullable=False)
    material_ytpe = db.Column(db.Integer, db.ForeignKey(
        RawMaterialType.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    batch_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)


class ProductionRawMaterialArrival(BaseModel):
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)
    arrival_id = db.Column(db.Integer, db.ForeignKey(
        RawMaterialArrival.id), nullable=False)


class ProductionShipping(BaseModel):
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)
    production_type = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)
    destination_id = db.Column(
        db.Integer, db.ForeignKey(Destination.id), nullable=False)
    shipping_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)


class InStockRawMaterial(StockModel):
    __table_args__ = (db.PrimaryKeyConstraint('arrival_id', 'material_type'),)

    arrival_id = db.Column(db.Integer, db.ForeignKey(RawMaterialArrival.id), primary_key=True)
    material_type = db.Column(db.Integer, db.ForeignKey(RawMaterialType.id), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

class InStockProduct(StockModel):
    __table_args__ = (db.PrimaryKeyConstraint('production_id', 'production_type'),)

    production_id = db.Column(db.Integer, db.ForeignKey(Production.id), primary_key=True)
    production_type = db.Column(db.Integer, db.ForeignKey(ProductionType.id), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)