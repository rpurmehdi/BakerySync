from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, Destination, ProductionShipment

destinations_bp = Blueprint(
    'destinations', __name__, url_prefix='/destinations')


@destinations_bp.route('/', methods=['GET', 'POST'])
def destinations():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        contact_person = request.form['contact_person'].title()
        contact_information = request.form['contact_information']
        type = request.form['type'].title()
        location = request.form['location'].title()
        description = request.form['description']

        # Create a new destination object and add it to the database
        new_destination = Destination(
            name=name,
            contact_person=contact_person,
            contact_information=contact_information,
            type=type,
            location=location,
            description=description
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_destination)
            db.session.commit()
            flash('New destination added successfully', 'success')
            # Redirect to the /destinations page
            return redirect(url_for('destinations.destinations'))

        except Exception as e:
            if 'UNIQUE constraint failed: destination.name' in str(e):
                flash(
                    f'Can not add another destination with the name {name}. destination name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('destinations.destinations'))

    else:
        # Retrieve all destinations from the database
        destinations = Destination.query.all()
        return render_template('destinations.html', destinations=destinations)


@destinations_bp.route('/edit', methods=['POST'])
def edit_destination():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        contact_person = request.form.get('contact_person')
        contact_information = request.form.get('contact_information')
        location = request.form.get('location')
        description = request.form.get('description')
        try:
            # Fetch the destination to edit from the database
            destination_to_edit = Destination.query.get(id)

            if destination_to_edit:
                # Update the destination with the new data
                destination_to_edit.contact_person = contact_person
                destination_to_edit.contact_information = contact_information
                destination_to_edit.location = location
                destination_to_edit.description = description

                # Commit the changes to the database
                db.session.commit()
                flash('Destination edited successfully', 'success')
            else:
                flash('Destination not found', 'danger')

                return redirect(url_for('destinations.destinations'))
        except Exception as e:
            if 'UNIQUE constraint failed: destination.name' in str(e):
                flash(
                    'Destination name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('destinations.destinations'))
    return redirect(url_for('destinations.destinations'))


@destinations_bp.route('/delete', methods=["POST"])
def delete_destination():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the destination by its ID
            destination_to_delete = Destination.query.get(id)

            if destination_to_delete:
                is_referenced = ProductionShipment.query.filter_by(
                    destination_id=id).first()
                if is_referenced:
                    flash(
                        f'{destination_to_delete.name} is used in shipments, cannot delete', 'danger')
                else:
                    # Delete the found destination
                    db.session.delete(destination_to_delete)
                    db.session.commit()
                    flash('Destination deleted successfully', 'success')
            else:
                flash('Destination not found', 'danger')

            # Redirect to the / page
            return redirect(url_for('destinations.destinations'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('destinations.destinations'))
    return redirect(url_for('destinations.destinations'))


@destinations_bp.route('/track/destination', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_destination(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('destinations.destinations'))
        

def track_destination(id):
    destination = Destination.query.get(id)
    shipped_types = set()
    for shipment in destination.shipments:
        production_type = shipment.production.type
        shipped_types.add(production_type)
    unique_types = list(shipped_types)
    return render_template('destinationtrack.html', destination=destination, shipped_types=unique_types)