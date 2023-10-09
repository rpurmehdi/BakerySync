from flask import flash, render_template, request, Blueprint, redirect, url_for
from datetime import datetime
from models import db, ProductionShipping, Destination, Production

shipments_bp = Blueprint('shipments', __name__, url_prefix='/shipments')


@shipments_bp.route('/', methods=['GET', 'POST'])
def shipments():
    if request.method == 'POST':
        # Get data from the form
        production_id = request.form['production_id']
        destination_id = request.form['destination_id']
        shipping_date_str = request.form['shipping_date']
        quantity_str = request.form['quantity']
        # validate form data
        production = Production.query.filter_by(
            id=production_id).first()
        destination = Destination.query.filter_by(
            id=destination_id).first()
        if production and destination:
            try:
                shipping_date = datetime.fromisoformat(shipping_date_str)
                quantity = float(quantity_str)
            except ValueError:
                flash('Invalid date or quantity format', 'danger')
                return redirect(url_for('shipments.shipments'))
            except Exception as e:
                flash(f'Error: {str(e)}', 'warning')
                return redirect(url_for('shipments.shipments'))
        else:
            flash('Invalid production or destination', 'warning')
            return redirect(url_for('shipments.shipments'))
        if quantity > production.stock:
            flash('Quantity is more than stock', 'warning')
            return redirect(url_for('shipments.shipments'))
        # Create a new shipment object and add it to the database
        new_shipment = ProductionShipping(
            production_id=production_id,
            destination_id=destination_id,
            shipping_date=shipping_date,
            quantity=quantity
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_shipment)
            db.session.commit()
            flash('New shipment added successfully', 'success')
            # Redirect to the /shipment page
            return redirect(url_for('shipments.shipments'))
        except Exception as e:

            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('shipments.shipments'))

    else:
        # Retrieve all shipments, productions and destinations from the database
        shipments = ProductionShipping.query.order_by(ProductionShipping.shipping_date).all()
        productions = Production.query.order_by(Production.type_id, Production.production_time).all()
        destinations = Destination.query.order_by(Destination.name).all()

        return render_template('shipments.html', shipments=shipments, productions=productions, destinations=destinations)


@shipments_bp.route('/edit', methods=['POST'])
def edit_shipment():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        production_id = request.form.get('production_id'),
        destination_id = request.form.get('destination_id'),
        shipping_date = request.form.get('shipping_date'),
        quantity = request.form.get('quantity')
        try:
            # Fetch the source to edit from the database
            shipment_to_edit = ProductionShipping.query.get(id)

            if shipment_to_edit:
                # Update the source with the new data
                shipment_to_edit.id = id
                shipment_to_edit.production_id = production_id
                shipment_to_edit.destination_id = destination_id
                shipment_to_edit.shipping_date = shipping_date
                shipment_to_edit.quantity = quantity
                # Commit the changes to the database
                db.session.commit()
                flash('Shipment edited successfully', 'success')
            else:
                flash('Shipment not found', 'danger')

                return redirect(url_for('shipments.shipments'))
        except Exception as e:

            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('shipments.shipments'))
    return redirect(url_for('shipments.shipments'))


@shipments_bp.route('/delete', methods=["POST"])
def delete_shipment():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the shipment by its ID
            shipment_to_delete = ProductionShipping.query.get(id)

            if shipment_to_delete:
                # Delete the found source
                db.session.delete(shipment_to_delete)
                db.session.commit()
                flash('Shipment deleted successfully', 'success')
            else:
                flash('Shipment not found', 'danger')

            # Redirect to the /sources page
            return redirect(url_for('shipments.shipments'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('shipments.shipments'))
    return redirect(url_for('shipments.shipments'))
