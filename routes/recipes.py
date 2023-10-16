from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import db, recipe_ingredient_association, Recipe, ProductionType, IngredientType, Production

recipes_bp = Blueprint('recipes', __name__, url_prefix='/recipes')


@recipes_bp.route('/', methods=['GET', 'POST'])
def recipes():
    if request.method == 'POST':
        # Get data from the form
        try:
            recipe_name = request.form['recipe_name'].capitalize()
            description = request.form['description']
            ptype = request.form['production_type']
            itypes = IngredientType.query.all()
            itype_percents = {}
            for itype in itypes:
                try:
                    itype_percent = float(request.form.get(itype.name, 0.0))
                except ValueError:
                    itype_percent = 0.0
                itype_percents[itype.name] = itype_percent
        except Exception as e:
            flash(f'Invalid data input! - Error: {str(e)}', 'warning')
            return redirect(url_for('recipes.recipes'))
        if recipe_name and ptype:
            try:
                production = ProductionType.query.get(ptype)
            except:
                flash('Invalid production type input!', 'warning')
                return redirect(url_for('recipes.recipes'))
        else:
            flash('Invalid data input!', 'warning')
            return redirect(url_for('recipes.recipes'))
        if sum(itype_percents.values()) != 100:
            flash(f'Invalid data input, percentages sum shouldbe 100 not {sum(itype_percents.values())}', 'warning')
            return redirect(url_for('recipes.recipes'))
        # Create a new recipe object and add it to the database
        new_recipe = Recipe(
            name=recipe_name,
            description=description,
            production_type=ptype,
        )
        duplicate_recipe = Recipe.query.filter_by(name=recipe_name, production_type=ptype).first()
        if duplicate_recipe:
            flash(
                    f'Can not add another recipe with the same name {recipe_name} for production type {ptype}. Recipe names must all be unique for each production.', 'warning')
            return redirect(url_for('recipes.recipes'))
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
            for itype in itypes:
                ing_percent = float(itype_percents[itype.name])
                if ing_percent != 0.0:
                    insertions.append(recipe_ingredient_association.insert().values(
                        recipe_id=new_recipe.id, ingredient_type=itype.id, quantity_percent=ing_percent))
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
        itypes = IngredientType.query.all()
        ingredients = db.session.query(recipe_ingredient_association).all()
        context = {
            'recipes': recipes,
            'ptypes': ptypes,
            'itypes': itypes,
            'ingredients': ingredients}

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
                    db.session.query(recipe_ingredient_association).filter(
                        recipe_ingredient_association.c.recipe_id == id).delete()
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
