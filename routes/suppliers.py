from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, Supplier, IngredientArrival

# blueprint to register in app.py
suppliers_bp = Blueprint('suppliers', __name__, url_prefix='/suppliers')

# route to handle show and add


@suppliers_bp.route('/', methods=['GET', 'POST'])
def suppliers():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        contact_person = request.form['contact_person'].title()
        contact_information = request.form['contact_information']
        type = request.form['type'].title()
        location = request.form['location'].title()
        description = request.form['description']

        # Create a new supplier object and add it to the database
        new_supplier = Supplier(
            name=name,
            contact_person=contact_person,
            contact_information=contact_information,
            type=type,
            location=location,
            description=description
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_supplier)
            db.session.commit()
            flash('New supplier added successfully', 'success')
            # Redirect to the /suppliers page
            return redirect(url_for('suppliers.suppliers'))

        except Exception as e:
            if 'UNIQUE constraint failed: supplier.name' in str(e):
                flash(
                    f'Can not add another supplier with the name {name}. Supplier name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('suppliers.suppliers'))

    else:
        # Retrieve all suppliers from the database
        suppliers = Supplier.query.all()
        return render_template('suppliers.html', suppliers=suppliers)

# route to handle edit


@suppliers_bp.route('/edit', methods=['POST'])
def edit_supplier():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        contact_person = request.form.get('contact_person')
        contact_information = request.form.get('contact_information')
        location = request.form.get('location')
        description = request.form.get('description')
        try:
            # Fetch the supplier to edit from the database
            supplier_to_edit = Supplier.query.get(id)

            if supplier_to_edit:
                # Update the supplier with the new data
                supplier_to_edit.contact_person = contact_person
                supplier_to_edit.contact_information = contact_information
                supplier_to_edit.location = location
                supplier_to_edit.description = description

                # Commit the changes to the database
                db.session.commit()
                flash('Supplier edited successfully', 'success')
            else:
                flash('Supplier not found', 'danger')

                return redirect(url_for('suppliers.suppliers'))
        except Exception as e:
            if 'UNIQUE constraint failed: supplier.name' in str(e):
                flash(
                    'Supplier name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('suppliers.suppliers'))
    return redirect(url_for('suppliers.suppliers'))

# route to handle delete


@suppliers_bp.route('/delete', methods=["POST"])
def delete_supplier():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the supplier by its ID
            supplier_to_delete = Supplier.query.get(id)

            if supplier_to_delete:
                is_referenced = IngredientArrival.query.filter_by(
                    supplier_id=id).first()
                if is_referenced:
                    flash(
                        f'{supplier_to_delete.name} is used in Arrivals, cannot delete', 'danger')
                else:
                    # Delete the found supplier
                    db.session.delete(supplier_to_delete)
                    db.session.commit()
                    flash('Supplier deleted successfully', 'success')
            else:
                flash('Supplier not found', 'danger')

            # Redirect to the /suppliers page
            return redirect(url_for('suppliers.suppliers'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('suppliers.suppliers'))
    return redirect(url_for('suppliers.suppliers'))

# route to handle track


@suppliers_bp.route('/track/supplier', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_supplier(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('suppliers.suppliers'))


def track_supplier(id):
    supplier = Supplier.query.get(id)
    arrived_types = [arrival.type for arrival in supplier.arrivals]
    unique_types = list(set(arrived_types))
    return render_template('suppliertrack.html', supplier=supplier, arrived_types=unique_types)
