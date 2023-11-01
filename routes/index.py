import json
import datetime
import calendar
from difflib import get_close_matches
from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import *

index_bp = Blueprint("index", __name__, url_prefix="")


@index_bp.route("/", methods=["GET", "POST"])
def index():
    # Dashboard
    if request.method == "GET":
        current_year = int(request.args.get("year", datetime.datetime.now().year))
        current_month = int(request.args.get("month", datetime.datetime.now().month))
        current_month_name = datetime.date(current_year, current_month, 1).strftime(
            "%B"
        )
        # keep track of all years included in database
        years = set()
        # arrivals of the month
        ingredients = IngredientType.query.order_by(IngredientType.name).all()
        month_arrivals = []
        for ingredient in ingredients:
            sum = 0
            for arrival in ingredient.arrivals:
                years.add(arrival.arriving_date.strftime("%Y"))
                if arrival.arriving_date.strftime("%y-%m-%d").startswith(
                    f"{current_year % 100:02d}-{current_month:02d}"
                ):
                    sum += arrival.quantity
            if sum > 0:
                month_arrivals.append((ingredient.name, sum))
        arrivals_json = json.dumps(month_arrivals)

        # shipments of the month
        shipmentsum = 0
        products = ProductType.query.order_by(ProductType.name).all()
        month_shipments = []
        month_productionsum = []
        for product in products:
            shipsum = 0
            for shipment in product.shipments:
                years.add(shipment.shipping_date.strftime("%Y"))
                if shipment.shipping_date.strftime("%Y-%m-%d").startswith(
                    f"{current_year}-{current_month:02d}"
                ):
                    shipsum += shipment.quantity
            if shipsum > 0:
                month_shipments.append((product.name, shipsum))
                shipmentsum += shipsum
            prdsum = 0
            for production in product.productions:
                years.add(production.production_time.strftime("%Y"))
                if production.production_time.strftime("%Y-%m-%d").startswith(
                    f"{current_year}-{current_month:02d}"
                ):
                    prdsum += production.quantity
            if prdsum > 0:
                month_productionsum.append((product.name, prdsum))
        shipments_json = json.dumps(month_shipments)
        productionsum_json = json.dumps(month_productionsum)

        # production / day in month
        productions = Production.query.all()

        # Generate a list of "YY-MM-DD" strings for each day in the current month
        days_in_month = calendar.monthrange(current_year, current_month)[1]
        days = [
            f"{current_year}-{current_month:02d}-{day:02d}"
            for day in range(1, days_in_month + 1)
        ]
        month_production = []
        datasum = 0
        for day in days:
            sum = 0
            for production in productions:
                if production.production_time.strftime("%Y-%m-%d").startswith(day):
                    sum += production.quantity
            datasum += sum
            month_production.append((day.split("-")[2], sum))
            if datasum > 0:
                productions_json = json.dumps(month_production)
            else:
                productions_json = []

        # ingredient stocks
        ingredienttypes = []
        for ingredient in ingredients:
            if ingredient.stock > 0:
                ingredienttypes.append((ingredient.name, ingredient.stock))
        ingredients_json = json.dumps(ingredienttypes)

        # product stocks
        producttypes = []
        for product in products:
            if product.stock > 0:
                producttypes.append((product.name, product.stock))
        products_json = json.dumps(producttypes)

        context = {
            "years": years,
            "datasum": datasum,
            "shipmentsum": shipmentsum,
            "productionsum": productionsum_json,
            "month": current_month_name,
            "year": current_year,
            "ingredients": ingredients_json,
            "products": products_json,
            "montharrivals": arrivals_json,
            "monthshipments": shipments_json,
            "monthproductions": productions_json,
        }
        return render_template("index.html", **context)

    # Track
    if request.method == "POST":
        # trackables
        trackables = []
        itypes = IngredientType.query.order_by(IngredientType.name).all()
        ptypes = ProductType.query.order_by(ProductType.name).all()
        sources = Source.query.order_by(Source.name).all()
        destinations = Destination.query.order_by(Destination.name).all()
        arrivals = IngredientArrival.query.order_by(
            IngredientArrival.arriving_date
        ).all()
        recipes = Recipe.query.all()
        productions = Production.query.order_by(Production.production_time).all()
        shipments = ProductShipment.query.order_by(ProductShipment.shipping_date).all()
        for itype in itypes:
            trackable = {
                "type": url_for("types.itrack"),
                "id": itype.id,
                "name": f"type: {itype.name}",
            }
            trackables.append(trackable)
        for ptype in ptypes:
            trackable = {
                "type": url_for("types.ptrack"),
                "id": ptype.id,
                "name": f"type: {ptype.name}",
            }
            trackables.append(trackable)
        for source in sources:
            trackable = {
                "type": url_for("sources.track"),
                "id": source.id,
                "name": f"source: {source.name}",
            }
            trackables.append(trackable)
        for destination in destinations:
            trackable = {
                "type": url_for("destinations.track"),
                "id": destination.id,
                "name": f"destination: {destination.name}",
            }
            trackables.append(trackable)
        for arrival in arrivals:
            trackable = {
                "type": url_for("arrivals.track"),
                "id": arrival.id,
                "name": f"arrival of {arrival.type.name} on {arrival.arriving_date.strftime('%Y-%m-%d')} from {arrival.source.name}",
            }
            trackables.append(trackable)
        for recipe in recipes:
            trackable = {
                "type": url_for("recipes.track"),
                "id": recipe.id,
                "name": f"{recipe.name} recipe for {recipe.type.name}",
            }
            trackables.append(trackable)
        for production in productions:
            trackable = {
                "type": url_for("productions.track"),
                "id": production.id,
                "name": f"production of {production.type.name} with batch {production.print_batch} on {production.production_time}",
            }
            trackables.append(trackable)
        for shipment in shipments:
            trackable = {
                "type": url_for("shipments.track"),
                "id": shipment.id,
                "name": f"shipment of {shipment.production.type.name} with batch {shipment.production.print_batch} on {shipment.shipping_date.strftime('%Y-%m-%d')} to {shipment.destination.name}",
            }
            trackables.append(trackable)
        try:
            search_query = request.form.get("track").lower()
            if len(search_query) < 3:
                flash("track query must be at least 3 characters long", "danger")
                return render_template("trackresult.html", results=[], search_query="")
            exact_matches = []
            partial_matchesh = []
            near_matches = []
            for trackable in trackables:
                name = trackable.get("name", "").lower()
                if name == search_query:
                    exact_matches.append(
                        {
                            "name": trackable["name"],
                            "id": trackable["id"],
                            "type": trackable["type"],
                        }
                    )
                elif search_query in name:
                    partial_matchesh.append(
                        {
                            "name": trackable["name"],
                            "id": trackable["id"],
                            "type": trackable["type"],
                        }
                    )
                elif get_close_matches(search_query, [name], n=1, cutoff=0.6):
                    near_matches.append(
                        {
                            "name": trackable["name"],
                            "id": trackable["id"],
                            "type": trackable["type"],
                        }
                    )
                results = []
                results.extend(exact_matches)
                results.extend(partial_matchesh)
                results.extend(near_matches)
            return render_template(
                "trackresult.html", results=results, search_query=search_query
            )
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            return render_template("trackresult.html", results=[], search_query="")
