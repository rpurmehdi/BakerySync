import json
from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import *
from routes.types import track_itype, track_ptype
from routes.sources import track_source
from routes.destinations import track_destination
from routes.arrivals import track_arrival
from routes.shipments import track_shipment
from routes.productions import track_production
from routes.recipes import track_recipe

index_bp = Blueprint(
    'index', __name__, url_prefix='')


@index_bp.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        # ingredient stocks
        ingredienttypes = []
        itypes = IngredientType.query.all()
        for itype in itypes:
            ingredienttypes.append((itype.name, itype.stock))
        ingredients_json = json.dumps(ingredienttypes)
        # production stocks
        productiontypes = []
        ptypes = ProductionType.query.all()
        for ptype in ptypes:
            productiontypes.append((ptype.name, ptype.stock))
        productions_json = json.dumps(productiontypes)
        return render_template("index.html", ingredients=ingredients_json, productions=productions_json)
    else:
        # trackables
        trackables = []
        itypes = IngredientType.query.all()
        ptypes = ProductionType.query.all()
        sources = Source.query.all()
        destinations = Destination.query.all()
        arrivals = IngredientArrival.query.all()
        recipes = Recipe.query.all()
        productions = Production.query.all()
        shipments = ProductionShipment.query.all()
        for itype in itypes:
            trackable = {
                "type": "itype",
                "id": itype.id,
                "name": itype.name,
            }
            trackables.append(trackable)
        for ptype in ptypes:
            trackable = {
                "type": "ptype",
                "id": ptype.id,
                "name": ptype.name,
            }
            trackables.append(trackable)
        for source in sources:
            trackable = {
                "type": "source",
                "id": source.id,
                "name": source.name,
            }
            trackables.append(trackable)
        for destination in destinations:
            trackable = {
                "type": "destination",
                "id": destination.id,
                "name": destination.name,
            }
            trackables.append(trackable)
        for arrival in arrivals:
            trackable = {
                "type": "arrival",
                "id": arrival.id,
                "name": f"{arrival.type.name} on {arrival.arriving_date} from {arrival.source.name}",
            }
            trackables.append(trackable)
        for recipe in recipes:
            trackable = {
                "type": "recipe",
                "id": recipe.id,
                "name": f"{recipe.name} recipe for {recipe.product.name}",
            }
            trackables.append(trackable)
        for production in productions:
            trackable = {
                "type": "production",
                "id": production.id,
                "name": f"{production.type.name} with batch {production.print_batch} on {production.production_time}",
            }
            trackables.append(trackable)
        for shipment in shipments:
            trackable = {
                "type": "shipment",
                "id": shipment.id,
                "name": f"{shipment.production.type.name} on {shipment.shipping_date} to {shipment.destination.name}",
            }
            trackables.append(trackable)
        function_map = {
            "arrival": track_arrival,
            "destination": track_destination,
            "production": track_production,
            "itype": track_itype,
            "ptype": track_ptype,
            "source": track_source,
            "shipment": track_shipment,
            "recipe": track_recipe
        }

        try:
            data_type = request.form.get('data-type')
            id = request.form.get('data-id')
            print(request.form.get('data-type'))
            print(request.form.get('data-id'))
            if data_type in function_map:
                return function_map[data_type](id)
            else:
                raise NameError("Invalid data type")
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('index.index'))
