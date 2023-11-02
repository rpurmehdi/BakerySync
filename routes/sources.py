from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, Source, IngredientArrival

# blueprint to register in app.py
sources_bp = Blueprint('sources', __name__, url_prefix='/sources')

# route to handle show and add


@sources_bp.route('/', methods=['GET', 'POST'])
def sources():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        contact_person = request.form['contact_person'].title()
        contact_information = request.form['contact_information']
        type = request.form['type'].title()
        location = request.form['location'].title()
        description = request.form['description']

        # Create a new source object and add it to the database
        new_source = Source(
            name=name,
            contact_person=contact_person,
            contact_information=contact_information,
            type=type,
            location=location,
            description=description
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_source)
            db.session.commit()
            flash('New source added successfully', 'success')
            # Redirect to the /sources page
            return redirect(url_for('sources.sources'))

        except Exception as e:
            if 'UNIQUE constraint failed: source.name' in str(e):
                flash(
                    f'Can not add another source with the name {name}. Source name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources.sources'))

    else:
        # Retrieve all sources from the database
        sources = Source.query.all()
        return render_template('sources.html', sources=sources)

# route to handle edit


@sources_bp.route('/edit', methods=['POST'])
def edit_source():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        contact_person = request.form.get('contact_person')
        contact_information = request.form.get('contact_information')
        location = request.form.get('location')
        description = request.form.get('description')
        try:
            # Fetch the source to edit from the database
            source_to_edit = Source.query.get(id)

            if source_to_edit:
                # Update the source with the new data
                source_to_edit.contact_person = contact_person
                source_to_edit.contact_information = contact_information
                source_to_edit.location = location
                source_to_edit.description = description

                # Commit the changes to the database
                db.session.commit()
                flash('Source edited successfully', 'success')
            else:
                flash('Source not found', 'danger')

                return redirect(url_for('sources.sources'))
        except Exception as e:
            if 'UNIQUE constraint failed: source.name' in str(e):
                flash(
                    'Source name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources.sources'))
    return redirect(url_for('sources.sources'))

# route to handle delete


@sources_bp.route('/delete', methods=["POST"])
def delete_source():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the source by its ID
            source_to_delete = Source.query.get(id)

            if source_to_delete:
                is_referenced = IngredientArrival.query.filter_by(
                    source_id=id).first()
                if is_referenced:
                    flash(
                        f'{source_to_delete.name} is used in Arrivals, cannot delete', 'danger')
                else:
                    # Delete the found source
                    db.session.delete(source_to_delete)
                    db.session.commit()
                    flash('Source deleted successfully', 'success')
            else:
                flash('Source not found', 'danger')

            # Redirect to the /sources page
            return redirect(url_for('sources.sources'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources.sources'))
    return redirect(url_for('sources.sources'))

# route to handle track


@sources_bp.route('/track/source', methods=['POST'])
def track():
    try:
        id = request.form.get("track")
        return track_source(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('sources.sources'))


def track_source(id):
    source = Source.query.get(id)
    arrived_types = [arrival.type for arrival in source.arrivals]
    unique_types = list(set(arrived_types))
    return render_template('sourcetrack.html', source=source, arrived_types=unique_types)
