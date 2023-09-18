import sqlite3
from flask import Flask, flash, redirect, render_template, request
import os


app = Flask(__name__)

pathdatabase = os.path.dirname(os.path.abspath(__file__)) 
class DatabaseError(Exception):
    pass

# Configure to use SQLite database
def db(sql_query, query_params=None, commit=True):
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(pathdatabase+'\Bakery.db')
        cursor = conn.cursor()

        # Execute the SQL query with optional parameters
        if query_params:
            cursor.execute(sql_query, query_params)
        else:
            cursor.execute(sql_query)

        if commit:
            conn.commit()  # Commit changes to the database for INSERT, UPDATE, DELETE

        # If it's a SELECT query, fetch and return the result
        if sql_query.strip().upper().startswith('SELECT'):
            rows = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]
            result = [dict(zip(column_names, row)) for row in rows]
            return result
        else:
            return None  # For INSERT, UPDATE, DELETE, return None

    except sqlite3.Error as e:
        flash(str(e), 'error')

    finally:
        # Close the cursor and the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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
        return 'Hi'

'''
EXAMPLE OF USING THE db FUNCTION FOR SQL QUERY:
# Example for SELECT
result = db("SELECT * FROM your_table")

# Example for INSERT
db("INSERT INTO your_table (column1, column2) VALUES (?, ?)", ('value1', 'value2'))

# Example for DELETE
db("DELETE FROM your_table WHERE column_name = ?", ('desired_column_name',), commit=True)

# Example for UPDATE
db("UPDATE your_table SET column1 = ?, column2 = ? WHERE condition_column = ?", ('new_value1', 'new_value2', 'condition_value'), commit=True)
'''