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

    arrivals = db.relationship('IngredientArrival', backref='source')


class Destination(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)
    contact_person = db.Column(db.String(255))
    contact_information = db.Column(db.String(255))
    type = db.Column(db.String(255))
    location = db.Column(db.String(255))
    description = db.Column(db.String(255))

    shipments = db.relationship('ProductionShipment', backref='destination')


recipe_ingredient_association = db.Table(
    'recipe_ingredient_association',
    db.Column('recipe_id', db.Integer, db.ForeignKey('recipe.id')),
    db.Column('ingredient_type', db.Integer,
              db.ForeignKey('ingredient_type.id')),
    db.Column('quantity_percent', db.Float)
)


class IngredientType(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)

    arrivals = db.relationship('IngredientArrival', backref='type')
    recipes = db.relationship(
        'Recipe', secondary=recipe_ingredient_association, back_populates='ingredients')

    @property
    def stock(self):
        total_stock = sum(arrival.stock for arrival in self.arrivals)
        return total_stock


production_arrival_association = db.Table(
    'production_arrival_association',
    db.Column('production_id', db.Integer,
              db.ForeignKey('production.id')),
    db.Column('arrival_id', db.Integer,
              db.ForeignKey('ingredient_arrival.id')),
    db.Column('quantity', db.Float)
)


class ProductionType(BaseModel):
    name = db.Column(db.String(255), unique=True, nullable=False)

    productions = db.relationship('Production', backref='type')
    recipes = db.relationship('Recipe', backref='product')

    @property
    def stock(self):
        total_stock = sum(production.stock for production in self.productions)
        return total_stock


class IngredientArrival(BaseModel):
    type_id = db.Column(db.Integer, db.ForeignKey(
        IngredientType.id), nullable=False)
    source_id = db.Column(db.Integer, db.ForeignKey(Source.id), nullable=False)
    arriving_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    productions = db.relationship(
        'Production',
        secondary=production_arrival_association,
        back_populates='ingredients'
    )

    @property
    def stock(self):
        total_usage = db.session.query(db.func.sum(production_arrival_association.c.quantity)).filter(
            production_arrival_association.c.arrival_id == self.id).scalar()
        stock = self.quantity - (total_usage or 0)
        return stock


class Recipe(BaseModel):
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255))
    production_type = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)

    ingredients = db.relationship(
        'IngredientType',
        secondary=recipe_ingredient_association,
        back_populates='recipes'
    )
    productions = db.relationship('Production', backref='recipe')

    def getp(self, ingredient_type_id):
        association = db.session.query(recipe_ingredient_association).filter(
            recipe_ingredient_association.c.recipe_id == self.id,
            recipe_ingredient_association.c.ingredient_type == ingredient_type_id
        ).first()

        if association:
            return association.quantity_percent
        return 0


class Production(BaseModel):
    print_batch = db.Column(db.String(255), unique=True, nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey(
        ProductionType.id), nullable=False)
    production_time = db.Column(db.DateTime, nullable=False)
    recipe_id = db.Column(db.Integer, db.ForeignKey(Recipe.id), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    shipments = db.relationship('ProductionShipment', backref='production')
    ingredients = db.relationship(
        'IngredientArrival',
        secondary=production_arrival_association,
        back_populates='productions'
    )

    @property
    def stock(self):
        total_shipment = sum(shipment.quantity for shipment in self.shipments)
        stock = self.quantity - total_shipment
        return stock


class ProductionShipment(BaseModel):
    production_id = db.Column(db.Integer, db.ForeignKey(
        Production.id), nullable=False)
    destination_id = db.Column(
        db.Integer, db.ForeignKey(Destination.id), nullable=False)
    shipping_date = db.Column(db.DateTime, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
