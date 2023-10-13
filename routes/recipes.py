from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, recipe_rawmaterial_association, Recipe, ProductionType, RawMaterialType, Production

recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@recipes_bp.route('/', methods=['GET', 'POST'])
def recipes():
    if request.method == 'POST':
        # Get data from the form
        try:
            recipe_name = request.form['recipe_name']
            description = request.form['description']
            ptype = request.form['production_type']
            rtypes = RawMaterialType.query.all()
            rtype_percents = {}
            for rtype in rtypes:
                rtype_percent = float(request.form.get(rtype.name, None))
                rtype_percents[rtype.name] = rtype_percent
        except Exception as e:
            flash(f'Invalid data input! - Error: {str(e)}', 'warning')
            return redirect(url_for('recipes.recipes'))
        if recipe_name and description and ptype:
            try:
                production = ProductionType.query.get(ptype)
            except:
                flash('Invalid production type input!', 'warning')
                return redirect(url_for('recipes.recipes'))
        else:
            flash('Invalid data input', 'warning')
            return redirect(url_for('recipes.recipes'))
        if sum(rtype_percents.values()) is not 100:
            flash('Invalid data input, percentages sum shouldbe 100', 'warning')
            return redirect(url_for('recipes.recipes'))
        # Create a new recipe object and add it to the database
        new_recipe = Recipe(
            name=recipe_name,
            description=description,
            ptype=ptype,
        )
        try:
            # Attempt to perform a database operation
            db.session.add(new_recipe)
            db.session.commit()
        except Exception as e:
            if 'UNIQUE constraint failed' in str(e):
                flash(
                    f'Can not add another recipe with the same name {recipe_name}. Recipe name must be unique.', 'warning')
            else:
                flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('recipes.recipes'))
        try:
            insertions = []
            for rtype in rtypes:
                raw_percent = int(rtype_percents[rtype.name])
                if raw_percent is not None:
                    insertions.append(recipe_rawmaterial_association.insert().values(
                        recipe_id=new_recipe.id, material_type=rtype.id, quantity_percent=raw_percent))
            for insertion in insertions:
                db.session.execute(insertion)
            db.session.commit()
            flash('New recipe added successfully', 'success')
            # Redirect to the / page
            return redirect(url_for('recipes.recipes'))
        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()
            db.session.delete(new_recipe)
            db.session.commit()
            return redirect(url_for('recipes.recipes'))
    else:
        # Retrieve all info from the database
        recipes = Recipe.query.all()
        ptypes = ProductionType.query.all()
        rtypes = RawMaterialType.query.all()
        materials = recipe_rawmaterial_association
        context = {
            'recipes': recipes,
            'ptypes': ptypes,
            'rtypes': ptypes,
            'materials': materials}

    return render_template('recipes.html', **context)


@recipes_bp.route('/delete', methods=["POST"])
def delete_recipe():
    if request.method == 'POST':
        id = request.form.get("id")
        try:
            # Attempt to find the recipe by its ID
            recipe_to_delete = Recipe.query.get(id)

            if recipe_to_delete:
                is_referenced = Production.query.filter_by(
                    recipe_id=id).first()
                if is_referenced:
                    flash(
                        f"{recipe_to_delete.name} is produced on {str(is_referenced.production_time)}, cannot delete", "danger")
                else:
                    db.session.query(recipe_rawmaterial_association).filter(
                        recipe_rawmaterial_association.c.recipe_id == id).delete()
                    db.session.delete(recipe_to_delete)
                    db.session.commit()
                    flash('Recipe deleted successfully', 'success')
            else:
                flash('Recipe not found', 'danger')

            # Redirect to the / page
            return redirect(url_for('recipes.recipes'))

        except Exception as e:
            flash(f'Error: {str(e)}', 'warning')
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for('recipes.recipes'))
    return redirect(url_for('recipes.recipes'))
