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


@app.route('/sources', methods=['GET', 'POST'])
def sources():
    if request.method == 'POST':
        # Get data from the form
        source_name = request.form['source_name']
        source_contact_person = request.form['source_contact_person']
        contact_information = request.form['contact_information']
        source_type = request.form['source_type']
        source_location = request.form['source_location']
        source_description = request.form['source_description']

        # Create a new source object and add it to the database
        new_source = Source(
            source_name=source_name,
            source_contact_person=source_contact_person,
            contact_information=contact_information,
            source_type=source_type,
            source_location=source_location,
            source_description=source_description
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_source)
            db.session.commit()
            flash('New source added successfully', 'success')
            # Redirect to the /sources page
            return redirect(url_for('sources'))

        except Exception as e:
            # Handle the exception and display an error message
            flash(f'Error: {str(e)}', 'error')
            db.session.rollback()  # Rollback any changes to the database

    else:
        # Retrieve all sources from the database
        sources = Source.query.all()
        return render_template('sources.html', sources=sources)


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


'''
EXAMPLE OF USING THE db FUNCTION FOR SQL QUERY:
# Example for SELECT


# Example for INSERT


# Example for DELETE


# Example for UPDATE
'''

if __name__ == '__main__':
    app.run(debug=True)
