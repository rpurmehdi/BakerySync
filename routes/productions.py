from flask import flash, render_template, request, Blueprint, redirect, url_for, jsonify
from datetime import datetime
from models import db, Production, RawMaterialArrival, ProductionShipment, production_arrival_association, Recipe, recipe_rawmaterial_association, ProductionType, RawMaterialType

productions_bp = Blueprint('productions', __name__, url_prefix='/productions')


@productions_bp.route('/', methods=['GET'])
def productions():
    productions = Production.query.all()
    recipe_data = db.session.query(production_arrival_association).all()
    return render_template('productions.html', productions=productions, recipe_data=recipe_data)


@productions_bp.route('/add', methods=['GET', 'POST'])
def add_production():
    if request.method == 'POST':
        # Get data from the form
        try:
            print_batch = request.form['batch_number']
            type_id = request.form['production_types']
            production_time_str = request.form['production_date']
            recipe_id = request.form['recipe']
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
            quantity=quantity
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_production)
            db.session.commit()
            flash('New production added successfully', 'success')
            # Redirect to the /productions page
            return redirect(url_for('productions.productions'))

        except Exception as e:
            if 'UNIQUE constraint failed: production.print_batch' in str(e):
                flash(
                    f'Can not add another production with the same {print_batch}. Production name must be unique. Please check dublicate production.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
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
                    # Delete the found production
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


@productions_bp.route('/usage', methods=["POST"])
def usage():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the production by its ID
            production = Production.query.get(id)
            recipe_data = db.session.query(production_arrival_association).all()
            if production:
                is_referenced = db.session.query(production_arrival_association).filter_by(production_id=id).first()
                if is_referenced:
                    flash(f'{production.type.name} with batch {production.print_batch} raw material already provided' , 'danger')
            else:
                flash('Production not found', 'danger')
                return redirect(url_for('productions.productions'))

            # Redirect to the / page
            return redirect(url_for('productions.productions'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('productions.productions'))
    return redirect(url_for('productions.productions'))