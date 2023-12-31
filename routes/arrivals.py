from flask import flash, render_template, request, Blueprint, redirect, url_for
from datetime import datetime
from models import db, IngredientType, IngredientArrival, Supplier, production_arrival_association

# blueprint to register in app.py
arrivals_bp = Blueprint('arrivals', __name__, url_prefix='/arrivals')

# route to handle show and add


@arrivals_bp.route('/', methods=['GET', 'POST'])
def arrivals():
    if request.method == 'POST':
        # Get data from the form
        type_id = request.form['type_id']
        supplier_id = request.form['supplier_id']
        arriving_date_str = request.form['arriving_date']
        quantity_str = request.form['quantity']
        # validate form data
        type = IngredientType.query.filter_by(
            id=type_id).first()
        supplier = Supplier.query.filter_by(
            id=supplier_id).first()
        if type and supplier:
            try:
                arriving_date = datetime.fromisoformat(arriving_date_str)
                quantity = float(quantity_str)
            except ValueError:
                flash('Invalid date or quantity format', 'danger')
                return redirect(url_for('arrivals.arrivals'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'warning')
                return redirect(url_for('arrivals.arrivals'))
        else:
            flash('Invalid type or supplier', 'warning')
            return redirect(url_for('arrivals.arrivals'))
        if quantity == 0 or quantity < (-1 * type.stock):
            flash('Quantity is invalid', 'warning')
            return redirect(url_for('arrivals.arrivals'))
        # Create a new arrival object and add it to the database
        new_arrival = IngredientArrival(
            type_id=type_id,
            supplier_id=supplier_id,
            arriving_date=arriving_date,
            quantity=quantity
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_arrival)
            db.session.commit()
            flash('New arrival added successfully', 'success')
            # Redirect to the /arrival page
            return redirect(url_for('arrivals.arrivals'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('arrivals.arrivals'))

    else:
        # Retrieve all arrivals, itypes and suppliers from the database
        arrivals = IngredientArrival.query.all()
        itypes = IngredientType.query.order_by(IngredientType.name).all()
        suppliers = Supplier.query.order_by(Supplier.name).all()
        context = {
            'arrivals': arrivals,
            'itypes': itypes,
            'suppliers': suppliers
        }
        return render_template('arrivals.html', **context)

# route to handle edit


@arrivals_bp.route('/edit', methods=['POST'])
def edit_arrival():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        type_id = request.form.get('type_id')
        supplier_id = request.form.get('supplier_id')
        arriving_date_str = request.form.get('arriving_date')
        quantity_str = request.form.get('quantity')
        # validate form data
        type = IngredientType.query.filter_by(
            id=type_id).first()
        supplier = Supplier.query.filter_by(
            id=supplier_id).first()
        if type and supplier:
            try:
                # Fetch the supplier to edit from the database
                arrival_to_edit = IngredientArrival.query.get(id)
                arriving_date = datetime.fromisoformat(arriving_date_str)
                quantity = float(quantity_str)
            except ValueError:
                flash('Invalid date or quantity format', 'danger')
                return redirect(url_for('arrivals.arrivals'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'warning')
                return redirect(url_for('arrivals.arrivals'))
        else:
            flash('Invalid type or supplier', 'warning')
            return redirect(url_for('arrivals.arrivals'))
        if arrival_to_edit:
            is_referenced = db.session.query(
                production_arrival_association).filter_by(arrival_id=id).first()
            if is_referenced:
                flash(
                    f'This {arrival_to_edit.type.name} is used in database, cannot edit', 'danger')
            else:
                try:
                    # Update the supplier with the new data
                    arrival_to_edit.id = id
                    arrival_to_edit.type_id = type_id
                    arrival_to_edit.supplier_id = supplier_id
                    arrival_to_edit.arriving_date = arriving_date
                    arrival_to_edit.quantity = quantity
                    # Commit the changes to the database
                    db.session.commit()
                    flash('Arrival edited successfully', 'success')
                except Exception as e:
                    flash(f'Error: {str(e)}', 'warning')
                    db.session.rollback()  # Rollback any changes to the database
        else:
            flash('Arrival not found', 'danger')
        return redirect(url_for('arrivals.arrivals'))
    return redirect(url_for('arrivals.arrivals'))

# route to handle delete


@arrivals_bp.route('/delete', methods=["POST"])
def delete_arrival():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the arrival by its ID
            arrival_to_delete = IngredientArrival.query.get(id)

            if arrival_to_delete:
                is_referenced = db.session.query(
                    production_arrival_association).filter_by(arrival_id=id).first()
                if is_referenced:
                    flash(
                        f'This {arrival_to_delete.type.name} is used in database, cannot delete', 'danger')
                else:
                    # Delete the found arrival
                    db.session.delete(arrival_to_delete)
                    db.session.commit()
                    flash('Arrival deleted successfully', 'success')
            else:
                flash('Arrival not found', 'danger')
            # Redirect to the / page
            return redirect(url_for('arrivals.arrivals'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('arrivals.arrivals'))
    return redirect(url_for('arrivals.arrivals'))

# route to handle track


@arrivals_bp.route('/track/arrival', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_arrival(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('arrivals.arrivals'))


def track_arrival(id):
    arrival = IngredientArrival.query.get(id)
    return render_template('arrivaltrack.html', arrival=arrival)
