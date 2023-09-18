import os
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, flash, redirect, render_template, request


app = Flask(__name__)

# Configure to use SQLalchemy database
# Create an SQLAlchemy engine for your database
path = os.path.dirname(os.path.abspath(__file__))
db_url = os.path.join(path, "bakerysync.db")
engine = create_engine(db_url)

# Reflect the database and generate Python classes for all tables
Base = automap_base()
Base.prepare(engine, reflect=True)

# Create a session to interact with the database
session = Session(engine)

def create_record(table, **kwargs):
    """Create a new record in the specified table."""
    try:
        new_record = table(**kwargs)
        session.add(new_record)
        session.commit()
        flash("Record created successfully", "success")
    except Exception as e:
        session.rollback()
        flash(f"Error creating record: {str(e)}", "error")

def read_records(table, filter_by=None):
    """Read records from the specified table."""
    try:
        if filter_by:
            records = session.query(table).filter_by(**filter_by).all()
        else:
            records = session.query(table).all()
        return records
    except Exception as e:
        flash(f"Error reading records: {str(e)}", "error")
        return []

def update_record(table, record_id, **kwargs):
    """Update an existing record with the provided values."""
    try:
        record = session.query(table).get(record_id)
        if record:
            for key, value in kwargs.items():
                setattr(record, key, value)
            session.commit()
            flash("Record updated successfully", "success")
        else:
            flash("Record not found", "error")
    except Exception as e:
        session.rollback()
        flash(f"Error updating record: {str(e)}", "error")

def delete_record(table, record_id):
    """Delete an existing record from the specified table."""
    try:
        record = session.query(table).get(record_id)
        if record:
            session.delete(record)
            session.commit()
            flash("Record deleted successfully", "success")
        else:
            flash("Record not found", "error")
    except Exception as e:
        session.rollback()
        flash(f"Error deleting record: {str(e)}", "error")

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
