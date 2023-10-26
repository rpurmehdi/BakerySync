import json
from difflib import get_close_matches
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
            if itype.stock > 0:
                ingredienttypes.append((itype.name, itype.stock))
        ingredients_json = json.dumps(ingredienttypes)
        # production stocks
        productiontypes = []
        ptypes = ProductionType.query.all()
        for ptype in ptypes:
            if ptype.stock > 0:
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
                "type": url_for('types.itrack'),
                "id": itype.id,
                "name": itype.name,
            }
            trackables.append(trackable)
        for ptype in ptypes:
            trackable = {
                "type": url_for('types.ptrack'),
                "id": ptype.id,
                "name": ptype.name,
            }
            trackables.append(trackable)
        for source in sources:
            trackable = {
                "type": url_for('sources.track'),
                "id": source.id,
                "name": source.name,
            }
            trackables.append(trackable)
        for destination in destinations:
            trackable = {
                "type": url_for('destinations.track'),
                "id": destination.id,
                "name": destination.name,
            }
            trackables.append(trackable)
        for arrival in arrivals:
            trackable = {
                "type": url_for('arrivals.track'),
                "id": arrival.id,
                "name": f"{arrival.type.name} on {arrival.arriving_date.strftime('%Y-%m-%d')} from {arrival.source.name}",
            }
            trackables.append(trackable)
        for recipe in recipes:
            trackable = {
                "type": url_for('recipes.track'),
                "id": recipe.id,
                "name": f"{recipe.name} recipe for {recipe.product.name}",
            }
            trackables.append(trackable)
        for production in productions:
            trackable = {
                "type": url_for('productions.track'),
                "id": production.id,
                "name": f"{production.type.name} with batch {production.print_batch} on {production.production_time}",
            }
            trackables.append(trackable)
        for shipment in shipments:
            trackable = {
                "type": url_for('shipments.track'),
                "id": shipment.id,
                "name": f"{shipment.production.type.name} on {shipment.shipping_date.strftime('%Y-%m-%d')} to {shipment.destination.name}",
            }
            trackables.append(trackable)
        try:
            search_query = request.form.get('track').lower()
            if len(search_query) < 3:
                flash('track query must be at least 3 characters long', 'danger')
                return redirect(url_for('index.index'))
            exact_matches = []
            partial_matchesh = []
            near_matches = []
            for trackable in trackables:
                name = trackable.get("name", "").lower()
                if name == search_query:
                    exact_matches.append(
                        {"name": trackable["name"], "id": trackable["id"], "type": trackable["type"]})
                elif search_query in name:
                    partial_matchesh.append(
                        {"name": trackable["name"], "id": trackable["id"], "type": trackable["type"]})
                elif get_close_matches(search_query, [name], n=1, cutoff=0.6):
                    near_matches.append(
                        {"name": trackable["name"], "id": trackable["id"], "type": trackable["type"]})
                results = []
                results.extend(exact_matches)
                results.extend(partial_matchesh)
                results.extend(near_matches)
            return render_template("trackresult.html", results=results)
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return redirect(url_for('index.index'))
