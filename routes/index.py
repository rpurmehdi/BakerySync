import json
import datetime
import calendar
from difflib import get_close_matches
from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import *

# blueprint to register in app.py
index_bp = Blueprint("index", __name__, url_prefix="")

# route to handle dashboard and track


@index_bp.route("/", methods=["GET", "POST"])
def index():
    # Dashboard
    if request.method == "GET":
        current_year = int(request.args.get(
            "year", datetime.datetime.now().year))
        current_month = int(request.args.get(
            "month", datetime.datetime.now().month))
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

        context = {
            "years": years,
            "datasum": datasum,
            "shipmentsum": shipmentsum,
            "productionsum": productionsum_json,
            "month": current_month_name,
            "year": current_year,
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
        suppliers = Supplier.query.order_by(Supplier.name).all()
        customers = Customer.query.order_by(Customer.name).all()
        arrivals = IngredientArrival.query.order_by(
            IngredientArrival.arriving_date
        ).all()
        recipes = Recipe.query.all()
        productions = Production.query.order_by(
            Production.production_time).all()
        shipments = ProductShipment.query.order_by(
            ProductShipment.shipping_date).all()
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
        for supplier in suppliers:
            trackable = {
                "type": url_for("suppliers.track"),
                "id": supplier.id,
                "name": f"supplier: {supplier.name}",
            }
            trackables.append(trackable)
        for customer in customers:
            trackable = {
                "type": url_for("customers.track"),
                "id": customer.id,
                "name": f"customer: {customer.name}",
            }
            trackables.append(trackable)
        for arrival in arrivals:
            trackable = {
                "type": url_for("arrivals.track"),
                "id": arrival.id,
                "name": f"arrival of {arrival.type.name} on {arrival.arriving_date.strftime('%Y-%m-%d')} from {arrival.supplier.name}",
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
                "name": f"shipment of {shipment.production.type.name} with batch {shipment.production.print_batch} on {shipment.shipping_date.strftime('%Y-%m-%d')} to {shipment.customer.name}",
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


@index_bp.route("/warehouse", methods=["GET"])
def warehouse():
    # ingredient stocks
    ingredients = IngredientType.query.order_by(IngredientType.name).all()
    ingredienttypes = []
    for ingredient in ingredients:
        if ingredient.stock > 0:
            ingredienttypes.append((ingredient.name, ingredient.stock))
    ingredients_json = json.dumps(ingredienttypes)

    # product stocks
    products = ProductType.query.order_by(ProductType.name).all()
    producttypes = []
    for product in products:
        if product.stock > 0:
            producttypes.append((product.name, product.stock))
    products_json = json.dumps(producttypes)

    context = {
        "ingredients": ingredients_json,
        "products": products_json,
    }
    return render_template("warehouse.html", **context)

# TEMP PERSIAN PREVIEW


@index_bp.route("/fa", methods=["GET"])
def fa():
    # Dashboard
    if request.method == "GET":
        current_year = int(request.args.get(
            "year", datetime.datetime.now().year))
        current_month = int(request.args.get(
            "month", datetime.datetime.now().month))
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
        if current_month == 11:
            shipments_json = [
                ["باگت", 300],
                ["بیگل", 50],
                ["پای سیب", 100],
                ["دونات", 80],
                ["کتاب", 250],
                ["کوکی بادامی", 175],
                ["کیک شکلاتی", 25],
                ["نان تست قهوه‌ای", 300],
                ["نان تست سفید", 210],
                ["فوکاچیا", 100],
            ]
            arrivals_json = [
                ["بادام درختی", 20],
                ["بیکینگ پودر", 15],
                ["روغن زیتون", 2],
                ["سیب", 30],
                ["شکر", 120],
                ["شیر", 10],
                ["کره", 50],
                ["گردو", 15],
                ["مخمر", 35],
                ["نمک", 55],
            ]
            productions_json = [
                ["01", 100],
                ["02", 150],
                ["03", 120],
                ["04", 50],
                ["05", 25],
                ["06", 80],
                ["07", 100],
                ["08", 100],
                ["09", 100],
                ["10", 0],
                ["11", 100],
                ["12", 130],
                ["13", 100],
                ["14", 210],
                ["15", 150],
                ["16", 0],
                ["17", 0],
                ["18", 0],
                ["19", 0],
                ["20", 0],
                ["21", 0],
                ["22", 0],
                ["23", 0],
                ["24", 0],
                ["25", 0],
                ["26", 0],
                ["27", 0],
                ["28", 0],
                ["29", 0],
                ["30", 0],
            ]
            productionsum_json = [
                ["باگت", 360],
                ["بیگل", 50],
                ["پای سیب", 100],
                ["دونات", 80],
                ["کتاب", 250],
                ["کوکی بادامی", 100],
                ["کیک شکلاتی", 25],
                ["نان تست قهوه‌ای", 370],
                ["نان تست سفید", 230],
                ["فوکاچیا", 100],
            ]
        else:
            shipments_json = []
            arrivals_json = []
            productionsum_json = []
            productions_json = []
        context = {
            "years": years,
            "datasum": datasum,
            "shipmentsum": shipmentsum,
            "productionsum": productionsum_json,
            "month": current_month_name,
            "year": current_year,
            "montharrivals": arrivals_json,
            "monthshipments": shipments_json,
            "monthproductions": productions_json,
        }
        return render_template("index-fa.html", **context)
