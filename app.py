import os
from flask import Flask, flash, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from models import db, Source, Destination, RawMaterialType, ProductionType, RawMaterialArrival, Recipe, Production, RawMaterialUsage, ProductionShipping, recipe_rawmaterial_association


app = Flask(__name__)

path = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(path, 'bakerysync.db')

app.secret_key = 'very_secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()


def create_tables():
    db.create_all()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        return render_template(
            "index.html"
        )
    else:
        return render_template("index.html")


@app.route('/sources', methods=['GET', 'POST'])
def sources():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        contact_person = request.form['contact_person']
        contact_information = request.form['contact_information']
        type = request.form['type']
        location = request.form['location']
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
            return redirect(url_for('sources'))

        except Exception as e:
            if 'UNIQUE constraint failed: source.name' in str(e):
                flash(
                    f'Can not add another source with the name {name}. Source name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources'))

    else:
        # Retrieve all sources from the database
        sources = Source.query.all()
        return render_template('sources.html', sources=sources)


@app.route('/edit_source', methods=['POST'])
def edit_source():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        name = request.form.get('name')
        contact_person = request.form.get('contact_person')
        contact_information = request.form.get('contact_information')
        type = request.form.get('type')
        location = request.form.get('location')
        description = request.form.get('description')
        try:
            # Fetch the source to edit from the database
            source_to_edit = Source.query.get(id)

            if source_to_edit:
                # Update the source with the new data
                source_to_edit.name = name
                source_to_edit.contact_person = contact_person
                source_to_edit.contact_information = contact_information
                source_to_edit.type = type
                source_to_edit.location = location
                source_to_edit.description = description

                # Commit the changes to the database
                db.session.commit()
                flash('Source edited successfully', 'success')
            else:
                flash('Source not found', 'danger')

                return redirect(url_for('sources'))
        except Exception as e:
            if 'UNIQUE constraint failed: source.name' in str(e):
                flash(
                    'Source name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources'))
    return redirect(url_for('sources'))


@app.route('/delete_source', methods=["POST"])
def delete_source():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the source by its ID
            source_to_delete = Source.query.get(id)

            if source_to_delete:
                is_referenced = RawMaterialArrival.query.filter_by(
                    source_id=id).first()
                if is_referenced:
                    flash('Source is used in Arrivals, cannot delete', 'danger')
                else:
                    # Delete the found source
                    db.session.delete(source_to_delete)
                    db.session.commit()
                    flash('Source deleted successfully', 'success')
            else:
                flash('Source not found', 'danger')

            # Redirect to the /sources page
            return redirect(url_for('sources'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('sources'))
    return redirect(url_for('sources'))


if __name__ == '__main__':
    app.run(debug=True)
