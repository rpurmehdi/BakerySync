from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, RawMaterialType, ProductionType, RawMaterialArrival, Recipe, Production, recipe_rawmaterial_association

types_bp = Blueprint('types', __name__, url_prefix='/types')


@types_bp.route('/', methods=['GET', 'POST'])
def types():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name'].capitalize()
        # Create a new type object and add it to the database
        if "rtype_form" in request.form:
            new_type = RawMaterialType(name=name)
        elif "ptype_form" in request.form:
            new_type = ProductionType(name=name)
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
        rtypes = RawMaterialType.query.all()
        ptypes = ProductionType.query.all()
        return render_template('types.html', rtypes=rtypes, ptypes=ptypes)


@types_bp.route('/edit', methods=['POST'])
def edit_type():
    if request.method == 'POST':
        # Get the data from the form
        id = request.form.get('id')
        name = request.form.get('name')
        try:
            if "rtype_edit" in request.form:
                type_to_edit = RawMaterialType.query.get(id)
            elif "ptype_edit" in request.form:
                type_to_edit = ProductionType.query.get(id)
            else:
                return redirect(url_for('types.types'))
        except:
            flash('Error reading the database', 'danger')
            return redirect(url_for('types.types'))
        try:
            if type_to_edit:
                if "rtype_edit" in request.form:
                    has_arrived = type_to_edit.arrivals
                    has_recipe = type_to_edit.recipes
                    if has_recipe:
                        flash(f"{type_to_edit.name} is used in recipe(s), cannot edit", "danger")
                        return redirect(url_for('types.types'))
                    if has_arrived:
                        flash(
                            f"{type_to_edit.name} has arrival(s), cannot edit", "danger")
                        return redirect(url_for('types.types'))    
                else:
                    has_production = type_to_edit.productions
                    has_recipe = type_to_edit.recipes
                if has_recipe:
                        flash(f"{type_to_edit.name} is used in recipe(s), cannot edit", "danger")
                        return redirect(url_for('types.types'))
                if has_production:
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
            if "rtype_delete" in request.form:
                id = request.form.get("rtype_delete")
                print(id)
                type_to_delete = RawMaterialType.query.get(id)
                raw = True
            elif "ptype_delete" in request.form:
                id = request.form.get("ptype_delete")
                type_to_delete = ProductionType.query.get(id)
                raw = False
            else:
                return redirect(url_for('types.types'))
        except:
            flash('Error reading the database', 'danger')
            return redirect(url_for('types.types'))
        try:
            if type_to_delete:
                if raw:
                    has_arrived = type_to_delete.arrivals
                    has_recipe = type_to_delete.recipes
                else:
                    has_production = type_to_delete.productions
                    has_recipe = type_to_delete.recipes
                if has_recipe:
                    flash(f"{type_to_delete.name} is used in recipe(s), cannot delete", "danger")
                    return redirect(url_for('types.types'))
                if raw and has_arrived:
                    flash(
                        f"{type_to_delete.name} has arrival(s), cannot delete", "danger")
                    return redirect(url_for('types.types'))
                if not raw and has_production:
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
