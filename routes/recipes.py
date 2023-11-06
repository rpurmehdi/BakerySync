from flask import flash, render_template, request, Blueprint, redirect, url_for
from models import (
    db,
    recipe_ingredient_association,
    Recipe,
    ProductType,
    IngredientType,
    Production,
)

# blueprint to register in app.py
recipes_bp = Blueprint("recipes", __name__, url_prefix="/recipes")

# route to handle show and add


@recipes_bp.route("/", methods=["GET", "POST"])
def recipes():
    if request.method == "POST":
        # Get data from the form
        try:
            recipe_name = request.form["recipe_name"].capitalize()
            description = request.form["description"]
            ptype = request.form["product"]
            itypes = IngredientType.query.all()
            itype_percents = {}
            for itype in itypes:
                try:
                    itype_percent = float(request.form.get(itype.name, 0.0))
                except ValueError:
                    itype_percent = 0.0
                itype_percents[itype.name] = itype_percent
        except Exception as e:
            flash(f"Invalid data input! - Error: {str(e)}", "warning")
            return redirect(url_for("recipes.recipes"))
        if recipe_name and ptype:
            try:
                product = ProductType.query.get(ptype)
            except:
                flash("Invalid product input!", "warning")
                return redirect(url_for("recipes.recipes"))
        else:
            flash("Invalid data input!", "warning")
            return redirect(url_for("recipes.recipes"))
        if sum(itype_percents.values()) != 100:
            flash(
                f"Invalid data input, percentages sum shouldbe 100 not {sum(itype_percents.values())}",
                "warning",
            )
            return redirect(url_for("recipes.recipes"))
        # Create a new recipe object and add it to the database
        new_recipe = Recipe(
            name=recipe_name,
            description=description,
            product=ptype,
        )
        duplicate_recipe = Recipe.query.filter_by(
            name=recipe_name, product=ptype
        ).first()
        if duplicate_recipe:
            flash(
                f"Can not add another recipe with the same name {recipe_name} for product {ptype}. Recipe names must all be unique for each production.",
                "warning",
            )
            return redirect(url_for("recipes.recipes"))
        try:
            # Attempt to perform a database operation
            db.session.add(new_recipe)
            db.session.commit()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                flash(
                    f"Can not add another recipe with the same name {recipe_name}. Recipe name must be unique.",
                    "warning",
                )
            else:
                flash(f"Error: {str(e)}", "warning")
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for("recipes.recipes"))
        try:
            insertions = []
            for itype in itypes:
                ing_percent = float(itype_percents[itype.name])
                if ing_percent != 0.0:
                    insertions.append(
                        recipe_ingredient_association.insert().values(
                            recipe_id=new_recipe.id,
                            ingredient_type=itype.id,
                            quantity_percent=ing_percent,
                        )
                    )
            for insertion in insertions:
                db.session.execute(insertion)
            db.session.commit()
            flash("New recipe added successfully", "success")
            # Redirect to the / page
            return redirect(url_for("recipes.recipes"))
        except Exception as e:
            flash(f"Error: {str(e)}", "warning")
            db.session.rollback()
            db.session.delete(new_recipe)
            db.session.commit()
            return redirect(url_for("recipes.recipes"))
    else:
        # Retrieve all info from the database
        recipes = Recipe.query.all()
        ptypes = ProductType.query.all()
        itypes = IngredientType.query.all()
        ingredients = db.session.query(recipe_ingredient_association).all()
        context = {
            "recipes": recipes,
            "ptypes": ptypes,
            "itypes": itypes,
            "ingredients": ingredients,
        }

    return render_template("recipes.html", **context)


# route to handle edit


@recipes_bp.route("/edit", methods=["POST"])
def edit_recipe():
    if request.method == "POST":
        # Get data from the form
        try:
            id = request.form["id"]
            recipe_name = request.form["edit-recipe-name"].capitalize()
            description = request.form["edit-description"]
            ptype = request.form["edit-product"]
            itypes = IngredientType.query.all()
            itype_percents = {}
            for itype in itypes:
                try:
                    itype_percent = float(request.form.get(itype.name, 0.0))
                except ValueError:
                    itype_percent = 0.0
                itype_percents[itype.name] = itype_percent
        except Exception as e:
            flash(f"Invalid data input! - Error: {str(e)}", "warning")
            return redirect(url_for("recipes.recipes"))
        if recipe_name and ptype:
            try:
                product = ProductType.query.get(ptype)
                recipe_to_edit = Recipe.query.get(id)
            except:
                flash("Invalid recipe or product input!", "warning")
                return redirect(url_for("recipes.recipes"))
        else:
            flash("Invalid data input!", "warning")
            return redirect(url_for("recipes.recipes"))
        if sum(itype_percents.values()) != 100:
            flash(
                f"Invalid data input, percentages sum shouldbe 100 not {sum(itype_percents.values())}",
                "warning",
            )
            return redirect(url_for("recipes.recipes"))
        # update values of recipe object and add it to the database
        recipe_to_edit.name = recipe_name
        recipe_to_edit.description = description
        recipe_to_edit.product = ptype
        duplicate_recipe = Recipe.query.filter_by(name=recipe_name, product=ptype).all()
        if len(duplicate_recipe) > 1:
            flash(
                f"Can not add another recipe with the same name {recipe_name} for product {ptype}. Recipe names must all be unique for each production.",
                "warning",
            )
            return redirect(url_for("recipes.recipes"))
        is_referenced = Production.query.filter_by(recipe_id=id).first()
        if is_referenced:
            flash(
                f"{recipe_to_edit.name} is produced on {str(is_referenced.production_time)}, cannot edit",
                "warning",
            )
            return redirect(url_for("recipes.recipes"))
        try:
            # Attempt to perform a database operation
            db.session.query(recipe_ingredient_association).filter(
                recipe_ingredient_association.c.recipe_id == id
            ).delete()
            db.session.commit()
        except Exception as e:
            if "UNIQUE constraint failed" in str(e):
                flash(
                    f"Can not add another recipe with the same name {recipe_name}. Recipe name must be unique.",
                    "warning",
                )
            else:
                flash(f"Error: {str(e)}", "warning")
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for("recipes.recipes"))
        try:
            insertions = []
            for itype in itypes:
                ing_percent = float(itype_percents[itype.name])
                if ing_percent != 0.0:
                    insertions.append(
                        recipe_ingredient_association.insert().values(
                            recipe_id=recipe_to_edit.id,
                            ingredient_type=itype.id,
                            quantity_percent=ing_percent,
                        )
                    )
            for insertion in insertions:
                db.session.execute(insertion)
            db.session.commit()
            flash("Recipe edited successfully", "success")
            # Redirect to the / page
            return redirect(url_for("recipes.recipes"))
        except Exception as e:
            flash(
                f"Error: {str(e)} CHECK PERCENTS FOR {recipe_to_edit.name}", "warning"
            )
            db.session.rollback()
            return redirect(url_for("recipes.recipes"))


# route to handle delete


@recipes_bp.route("/delete", methods=["POST"])
def delete_recipe():
    if request.method == "POST":
        id = request.form.get("id")
        try:
            # Attempt to find the recipe by its ID
            recipe_to_delete = Recipe.query.get(id)

            if recipe_to_delete:
                is_referenced = Production.query.filter_by(recipe_id=id).first()
                if is_referenced:
                    flash(
                        f"{recipe_to_delete.name} is produced on {str(is_referenced.production_time)}, cannot delete",
                        "danger",
                    )
                else:
                    db.session.query(recipe_ingredient_association).filter(
                        recipe_ingredient_association.c.recipe_id == id
                    ).delete()
                    db.session.delete(recipe_to_delete)
                    db.session.commit()
                    flash("Recipe deleted successfully", "success")
            else:
                flash("Recipe not found", "danger")

            # Redirect to the / page
            return redirect(url_for("recipes.recipes"))

        except Exception as e:
            flash(f"Error: {str(e)}", "warning")
            db.session.rollback()  # Rollback any changes to the database
            return redirect(url_for("recipes.recipes"))
    return redirect(url_for("recipes.recipes"))


# route to handle track


@recipes_bp.route("/track/recipe", methods=["POST"])
def track():
    try:
        id = request.form.get("track")
        return track_recipe(id)
    except Exception as e:
        flash(f"Database error: {str(e)}", "danger")
        return redirect(url_for("recipes.recipes"))


def track_recipe(id):
    recipe = Recipe.query.get(id)
    return render_template("recipetrack.html", recipe=recipe)
