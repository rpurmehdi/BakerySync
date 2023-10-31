from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, IngredientType, ProductType, production_arrival_association, recipe_ingredient_association

types_bp = Blueprint('types', __name__, url_prefix='/types')


@types_bp.route('/', methods=['GET', 'POST'])
def types():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        # Create a new type object and add it to the database
        if "itype_form" in request.form:
            new_type = IngredientType(name=name)
        elif "ptype_form" in request.form:
            new_type = ProductType(name=name)
        else:
            return redirect(url_for('types.types'))
        try:
            # Attempt to perform a database operation
            db.session.add(new_type)
            db.session.commit()
            flash('New Type added successfully', 'success')
            # Redirect to the types page
            return redirect(url_for('types.types'))
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                flash(
                    f'Can not add another type with the name {name}. Type name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('types.types'))
    else:
        # Retrieve all types from the database
        itypes = IngredientType.query.all()
        ptypes = ProductType.query.all()
        return render_template('types.html', itypes=itypes, ptypes=ptypes)


@types_bp.route('/edit', methods=['POST'])
def edit_type():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        name = request.form.get('name')
        try:
            if "itype_edit" in request.form:
                type_to_edit = IngredientType.query.get(id)
                ing = True
            elif "ptype_edit" in request.form:
                type_to_edit = ProductType.query.get(id)
                ing = False
            else:
                return redirect(url_for('types.types'))
        except:
            flash('Error reading the database', 'danger')
            return redirect(url_for('types.types'))
        try:
            if type_to_edit:
                if ing:
                    has_use = type_to_edit.arrivals
                    has_recipe = type_to_edit.recipes
                else:
                    has_use = type_to_edit.productions
                    has_recipe = type_to_edit.recipes
                if has_recipe:
                    flash(
                        f"{type_to_edit.name} is used in recipe(s), cannot edit", "danger")
                    return redirect(url_for('types.types'))
                if ing and has_use:
                    flash(
                        f"{type_to_edit.name} has arrival(s), cannot edit", "danger")
                    return redirect(url_for('types.types'))
                if not ing and has_use:
                    flash(
                        f"{type_to_edit.name} has been produced, cannot edit", "danger")
                    return redirect(url_for('types.types'))
                # edit the found type
                type_to_edit.name = name
                db.session.commit()
                flash('Type edited successfully', 'success')
            else:
                flash('Type not found', 'danger')
            return redirect(url_for('types.types'))
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                flash(
                    f'Can not have another type with the name {name}. Type name must be unique. Please choose a different name.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('types.types'))
    else:
        return redirect(url_for('types.types'))


@types_bp.route('/delete', methods=["POST"])
def delete_type():
    if request.method == 'POST':
        try:
            if "itype_delete" in request.form:
                id = request.form.get("itype_delete")
                print(id)
                type_to_delete = IngredientType.query.get(id)
                ing = True
            elif "ptype_delete" in request.form:
                id = request.form.get("ptype_delete")
                type_to_delete = ProductType.query.get(id)
                ing = False
            else:
                return redirect(url_for('types.types'))
        except:
            flash('Error reading the database', 'danger')
            return redirect(url_for('types.types'))
        try:
            if type_to_delete:
                if ing:
                    has_use = type_to_delete.arrivals
                    has_recipe = type_to_delete.recipes
                else:
                    has_use = type_to_delete.productions
                    has_recipe = type_to_delete.recipes
                if has_recipe:
                    flash(
                        f"{type_to_delete.name} is used in recipe(s), cannot delete", "danger")
                    return redirect(url_for('types.types'))
                if ing and has_use:
                    flash(
                        f"{type_to_delete.name} has arrival(s), cannot delete", "danger")
                    return redirect(url_for('types.types'))
                if not ing and has_use:
                    flash(
                        f"{type_to_delete.name} has been produced, cannot delete", "danger")
                    return redirect(url_for('types.types'))
                # Delete the found type
                db.session.delete(type_to_delete)
                db.session.commit()
                flash('Type deleted successfully', 'success')
            else:
                flash('Type not found', 'danger')
            return redirect(url_for('types.types'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('types.types'))
    else:
        return redirect(url_for('sources.sources'))


@types_bp.route('/track/ingredient', methods=['POST'])
def itrack():
    try:
        id = request.form.get("track")
        return track_itype(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('types.types'))


def track_itype(id):
    ingredient = IngredientType.query.get(id)
    return render_template('itypetrack.html', ingredient=ingredient)


@types_bp.route('/track/product', methods=['POST'])
def ptrack():
    try:
        id = request.form.get("track")
        return track_ptype(id)
    except Exception as e:
        flash(f'Database error: {str(e)}', 'danger')
        return redirect(url_for('types.types'))


def track_ptype(id):
    product = ProductType.query.get(id)
    return render_template('ptypetrack.html', product=product)
