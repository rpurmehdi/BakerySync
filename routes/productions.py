import logging
from flask import flash, render_template, request, Blueprint, redirect, url_for, jsonify
from datetime import datetime
from models import db, Production, RawMaterialArrival, ProductionShipment, production_arrival_association, Recipe, recipe_rawmaterial_association, ProductionType, RawMaterialType

productions_bp = Blueprint('productions', __name__, url_prefix='/productions')


@productions_bp.route('/', methods=['GET'])
def productions():
    productions = Production.query.all()
    return render_template('productions.html', productions=productions)


@productions_bp.route('/add', methods=['GET', 'POST'])
def add_production():
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
        if quantity < 1:
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
            for material in recipe.materials:
                raw_quant = int(request.form[material.name])
                if raw_quant > material.stock:
                    raise ValueError(
                        f"{material.name} quantity can not be more than stock")
                sorted_arrivals = sorted(
                    material.arrivals, key=lambda material: material.arriving_date)
                for arrival in sorted_arrivals:
                    if raw_quant > 0:
                        arr_stock = arrival.stock
                        if arr_stock > raw_quant:
                            insertions.append(production_arrival_association.insert().values(
                                production_id=new_production.id, arrival_id=arrival.id, quantity=raw_quant))
                            raw_quant = 0
                        elif arr_stock > 0:
                            insertions.append(production_arrival_association.insert().values(
                                production_id=new_production.id, arrival_id=arrival.id, quantity=arr_stock))
                            raw_quant = raw_quant - arr_stock
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
        rtypes = RawMaterialType.query.all()
        materials = RawMaterialArrival.query.order_by(
            RawMaterialArrival.arriving_date, RawMaterialArrival.type_id).all()
        recipes = Recipe.query.all()
        return render_template('add_production.html', materials=materials, recipes=recipes,  productions=productions, ptypes=ptypes, rtypes=rtypes)


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
                        f'{production_to_delete.type.name} with batch {production_to_delete.print_batch} is used in Shipments, cannot delete', 'danger')
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

    ids = []
    names = []
    percents = []
    stocks = []
    for material in recipe.materials:
        ids.append(material.id)
        names.append(material.name)
        percents.append(recipe.getp(material.id))
        stocks.append(material.stock)
    response = {
        'ids': ids,
        'names': names,
        'percents': percents,
        'stocks': stocks
    }

    return jsonify(response)
