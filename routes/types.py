from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, RawMaterialType, ProductionType, RawMaterialArrival, Recipe, Production, recipe_rawmaterial_association

types_bp = Blueprint('types', __name__, url_prefix='/types')


@types_bp.route('/', methods=['GET', 'POST'])
def types():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
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
            flash('New Typr added successfully', 'success')
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
                type_to_edit.name = name
                # Commit the changes to the database
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
        id = request.form.get("id")
        try:
            if "rtype_delete" in request.form:
                type_to_delete = RawMaterialType.query.get(id)
            elif "ptype_delete" in request.form:
                type_to_delete = ProductionType.query.get(id)
            else:
                return redirect(url_for('types.types'))
        except:
            flash('Error reading the database', 'danger')
            return redirect(url_for('types.types'))
        try:
            if type_to_delete:
                if "rtype_delete" in request.form:
                    is_referenced = RawMaterialArrival.query.filter_by(type=id).count(
                    ) + db.session.query(recipe_rawmaterial_association).filter_by(material_type=id).count()
                else:
                    is_referenced = Recipe.query.filter_by(
                        production_type=id).count() + Production.query.filter_by(type=id).count()
                if is_referenced and is_referenced > 0:
                    flash(
                        f'{type_to_delete.name} is used in database, cannot delete', 'danger')
                else:
                    # Delete the found type
                    db.session.delete(type_to_delete)
                    db.session.commit()
                    flash('Type deleted successfully', 'success')
            else:
                flash('Type not found', 'danger')
            # Redirect to the / page
            return redirect(url_for('types.types'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('types.types'))
    else:
        return redirect(url_for('sources.sources'))
