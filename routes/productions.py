import random
from flask import flash, render_template, request, Blueprint, redirect, url_for, jsonify
from datetime import datetime
from models import db, Production, IngredientArrival, ProductionShipment, production_arrival_association, Recipe, ProductionType, IngredientType

productions_bp = Blueprint('productions', __name__, url_prefix='/productions')


@productions_bp.route('/', methods=['GET', 'POST'])
def productions():
    if request.method == 'POST':
        # Get data from the form
        try:
            print_batch = request.form['batch_number']
            type_id = request.form['production_types']
            production_time_str = request.form['production_date']
            recipe_id = request.form["recipe" + str(type_id)]
            quantity_str = request.form['quantity']
        except Exception as e:
            flash(f'Invalid data input! - Error: {str(e)}', 'warning')
            return redirect(url_for('productions.productions'))
        if print_batch and quantity_str:
            try:
                production_time = datetime.fromisoformat(production_time_str)
                quantity = float(quantity_str)
            except ValueError:
                flash('Invalid date or quantity format', 'danger')
                return redirect(url_for('productions.productions'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'warning')
                return redirect(url_for('productions.productions'))
        else:
            flash('Invalid data input', 'warning')
            return redirect(url_for('productions.productions'))
        if quantity < 0.1:
            flash('Invalid data input', 'warning')
            return redirect(url_for('productions.productions'))
        # Create a new production object and add it to the database
        new_production = Production(
            print_batch=print_batch,
            type_id=type_id,
            production_time=production_time,
            recipe_id=recipe_id,
            quantity=quantity)
        try:
            # Attempt to perform a database operation
            recipe = Recipe.query.get(recipe_id)
            db.session.add(new_production)
            db.session.commit()
        except Exception as e:
            if 'UNIQUE constraint failed: production.print_batch' in str(e):
                flash(
                    f'Can not add another production with the same {print_batch}. Production name must be unique. Please check dublicate production.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('productions.productions'))
        try:
            insertions = []
            for ingredient in recipe.ingredients:
                ing_quant = float(request.form[ingredient.name])
                if ing_quant > ingredient.stock:
                    raise ValueError(
                        f"{ingredient.name} quantity can not be more than stock")
                sorted_arrivals = sorted(
                    ingredient.arrivals, key=lambda ingredient: ingredient.arriving_date)
                for arrival in sorted_arrivals:
                    if ing_quant > 0:
                        arr_stock = arrival.stock
                        if arr_stock > ing_quant:
                            insertions.append(production_arrival_association.insert().values(
                                production_id=new_production.id, arrival_id=arrival.id, quantity=ing_quant))
                            ing_quant = 0
                        elif arr_stock > 0:
                            insertions.append(production_arrival_association.insert().values(
                                production_id=new_production.id, arrival_id=arrival.id, quantity=arr_stock))
                            ing_quant = ing_quant - arr_stock
            for insertion in insertions:
                db.session.execute(insertion)
            db.session.commit()
            flash('New production added successfully', 'success')
            # Redirect to the / page
            return redirect(url_for('productions.productions'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()
            db.session.delete(new_production)
            db.session.commit()
            return redirect(url_for('productions.productions'))
    else:
        # Retrieve all info from the database
        productions = Production.query.all()
        ptypes = ProductionType.query.all()
        rtypes = IngredientType.query.all()
        ingredients = IngredientArrival.query.order_by(
            IngredientArrival.arriving_date, IngredientArrival.type_id).all()
        recipes = Recipe.query.all()
        # make random colors
        colors = []
        for i in range(100):
            if i < 50:
                red = random.randint(0, 150)
                green = random.randint(50, 255)
                blue = random.randint(50, 255)
                rgba = f"rgba({red}, {green}, {blue}, 0.5)"
                colors.append(rgba)
            else:
                rgba = colors[i-50].replace("0.5", "1")
                colors.append(rgba)
    context = {
        'ingredients': ingredients,
        'recipes': recipes,
        'productions': productions,
        'ptypes': ptypes,
        'rtypes': rtypes,
    }
    return render_template('productions.html', **context)


@productions_bp.route('/delete', methods=["POST"])
def delete_production():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the production by its ID
            production_to_delete = Production.query.get(id)

            if production_to_delete:
                is_referenced = ProductionShipment.query.filter_by(
                    production_id=id).first()
                if is_referenced:
                    flash(
                        f"{production_to_delete.type.name} with batch {production_to_delete.print_batch} is shipped on {str(is_referenced.shipping_date)}, cannot delete", "danger")
                else:
                    db.session.query(production_arrival_association).filter(
                        production_arrival_association.c.production_id == id).delete()
                    db.session.delete(production_to_delete)
                    db.session.commit()
                    flash('Production deleted successfully', 'success')
            else:
                flash('Production not found', 'danger')

            # Redirect to the / page
            return redirect(url_for('productions.productions'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('productions.productions'))
    return redirect(url_for('productions.productions'))


@productions_bp.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    if 'data' not in data:
        return jsonify({'error': 'Recipe ID not provided'}), 400

    recipe = Recipe.query.get(data['data'])
    if recipe is None:
        return jsonify({'error': 'Recipe not found'}), 404
    sorted_ingredients = sorted(
        recipe.ingredients, key=lambda ingredient: recipe.getp(ingredient.id), reverse=True)
    ids = []
    names = []
    percents = []
    stocks = []
    for ingredient in sorted_ingredients:
        ids.append(ingredient.id)
        names.append(ingredient.name)
        percents.append(recipe.getp(ingredient.id))
        stocks.append(ingredient.stock)
    response = {
        'ids': ids,
        'names': names,
        'percents': percents,
        'stocks': stocks
    }

    return jsonify(response)


@productions_bp.route('/track/production', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_production(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('productions.productions'))


def track_production(id):
    production = Production.query.get(id)
    return render_template('productiontrack.html', production=production)
