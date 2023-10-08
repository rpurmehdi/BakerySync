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

    arrivals = db.relationship('RawMaterialArrival', backref='kind')
    recipes = db.relationship(
        'Recipe', secondary=recipe_rawmaterial_association, back_populates='materials')

    @property
    def stock(self):
        total_stock = sum(arrival.stock for arrival in self.arrivals)
        return total_stock


production_arrival_association = db.Table(
    'production_arrival_association',
    db.Column('production_id', db.Integer,
              db.ForeignKey('production.id')),
    db.Column('arrival_id', db.Integer,
              db.ForeignKey('raw_material_arrival.id')),
    db.Column('quantity', db.Float)
)


class ProductionType(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)

    productions = db.relationship('Production', backref='kind')
    recipes = db.relationship('Recipe', backref='product')

    @property
    def stock(self):
        total_stock = sum(production.stock for production in self.productions)
        return total_stock


class RawMaterialArrival(BaseModel):
    type = db.Column(db.Integer, db.ForeignKey(
        RawMaterialType.id), nullable=False)
    arrival_time = db.Column(db.DateTime, nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Source.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    productions = db.relationship(
        'Production',
        secondary=production_arrival_association,
        back_populates='materials'
    )

    @property
    def stock(self):
        total_usage = sum(association.quantity for association in self.productions)
        stock = self.quantity - total_usage
        return stock


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

    shippings = db.relationship('ProductionShipping', backref='production')
    materials = db.relationship(
        'RawMaterialArrival',
        secondary=production_arrival_association,
        back_populates='productions'
    )

    @property
    def stock(self):
        total_shipping = sum(shipment.quantity for shipment in self.shippings)
        stock = self.quantity - total_shipping
        return stock


class ProductionShipping(BaseModel):
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)
    destination_id = db.Column(
        db.Integer, db.ForeignKey(Destination.id), nullable=False)
    shipping_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
