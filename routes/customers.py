from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, Customer, ProductShipment

# blueprint to register in app.py
customers_bp = Blueprint(
    'customers', __name__, url_prefix='/customers')

# route to handle show and add


@customers_bp.route('/', methods=['GET', 'POST'])
def customers():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        contact_person = request.form['contact_person'].title()
        contact_information = request.form['contact_information']
        type = request.form['type'].title()
        location = request.form['location'].title()
        description = request.form['description']

        # Create a new customer object and add it to the database
        new_customer = Customer(
            name=name,
            contact_person=contact_person,
            contact_information=contact_information,
            type=type,
            location=location,
            description=description
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_customer)
            db.session.commit()
            flash('New customer added successfully', 'success')
            # Redirect to the /customers page
            return redirect(url_for('customers.customers'))

        except Exception as e:
            if 'UNIQUE constraint failed: customer.name' in str(e):
                flash(
                    f'Can not add another customer with the name {name}. customer name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('customers.customers'))

    else:
        # Retrieve all customers from the database
        customers = Customer.query.all()
        return render_template('customers.html', customers=customers)

# route to handle edit


@customers_bp.route('/edit', methods=['POST'])
def edit_customer():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        contact_person = request.form.get('contact_person')
        contact_information = request.form.get('contact_information')
        location = request.form.get('location')
        description = request.form.get('description')
        try:
            # Fetch the customer to edit from the database
            customer_to_edit = Customer.query.get(id)

            if customer_to_edit:
                # Update the customer with the new data
                customer_to_edit.contact_person = contact_person
                customer_to_edit.contact_information = contact_information
                customer_to_edit.location = location
                customer_to_edit.description = description

                # Commit the changes to the database
                db.session.commit()
                flash('Customer edited successfully', 'success')
            else:
                flash('Customer not found', 'danger')

                return redirect(url_for('customers.customers'))
        except Exception as e:
            if 'UNIQUE constraint failed: customer.name' in str(e):
                flash(
                    'Customer name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('customers.customers'))
    return redirect(url_for('customers.customers'))

# route to handle delete


@customers_bp.route('/delete', methods=["POST"])
def delete_customer():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the customer by its ID
            customer_to_delete = Customer.query.get(id)

            if customer_to_delete:
                is_referenced = ProductShipment.query.filter_by(
                    customer_id=id).first()
                if is_referenced:
                    flash(
                        f'{customer_to_delete.name} is used in shipments, cannot delete', 'danger')
                else:
                    # Delete the found customer
                    db.session.delete(customer_to_delete)
                    db.session.commit()
                    flash('Customer deleted successfully', 'success')
            else:
                flash('Customer not found', 'danger')

            # Redirect to the / page
            return redirect(url_for('customers.customers'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('customers.customers'))
    return redirect(url_for('customers.customers'))

# route to handle track


@customers_bp.route('/track/customer', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_customer(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('customers.customers'))


def track_customer(id):
    customer = Customer.query.get(id)
    shipped_types = set()
    for shipment in customer.shipments:
        product = shipment.production.type
        shipped_types.add(product)
    unique_types = list(shipped_types)
    return render_template('customertrack.html', customer=customer, shipped_types=unique_types)
