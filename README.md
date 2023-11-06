# BAKERYSYNC ERP SYSTEM
#### Video Demo:  <https://youtu.be/e4A_-b8avaQ>
#### Description:
BakerySync is a web-based management system designed for bakeries to streamline production, track inventory, and manage ingredient arrivals and shipments efficiently. It provides bakery managers with tools to monitor and optimize their operations, saving them time and money, improving efficiency, and reducing waste.
BakerySync is built using Python and the Flask microframework. It uses a SQLite database to store data, and its front-end is rendered using Jinja2 templates.
#### Getting Started:
Follow these instructions to get BakerySync up and running on your local machine.
 - **Prerequisites**:
- Python 3.x
- Flask
- Flask-SQLAlchemy
 - **how to run**:
 after installing the prerequisites, run app.py via python and go to localhost:5000 on your browser. Alternatively you can deploy it to a WSGI server, which is a fast application server written in C.
## Features
- **Production Management**: Easily create, edit, and track bakery production batches. Each production batch can be associated with a recipe, production type, and ingredients used. you can also track the suppliers you got that ingredients from. this makes batch tracking to a whole new level.
- **Inventory**: Keep an eye on your bakery's inventory by monitoring stock levels for different ingredients and products. Bakerysync uses FIFO when handling ingredient usage from inventory, ensuring what comes first, is used first.
- **Ingredient Arrivals**: Record and manage the arrival of ingredients from suppliers and the suppliers themselves, ensuring that you have the right ingredients at the right time.
- **Product Shipment**: Record and manage the shipments of bakery products to different customers. Keep an organized record of where your products are headed and who your customers are.
- **Recipe Management**: Manage recipes that define the ingredients and quantities needed for each bakery product.
- **Track function**: Track every single event that has happened in your bakery; whether it's an ingredient you want to know where it has been used or a recipe you want to know how many times you have shipped the products that where made by using it. Everything is connected and analysable with track function.
## Structure
The BakerySync codebase is organized into the following files and folders:
#### app.py
app.py is the main file of the application, it contains the configurations and run commands for Flask such as database location and creation, database tables creation and import, and custom jinja template filters.
#### models.py
This file contains the classes for SQLAlchemy, which will be created as SQL tables at the first run of the main app. BaseModel is the base class defined, and other classes are its children. There are also two association tables that are created to handle many-to-many relationships between other classes (recipe_ingredient_association for relationship between IngredientType and Recipe, and production_arrival_association for relationship between ProductType and IngredientArrival).
#### templates folder
The templates folder contains the HTML files for render_template, which is a Flask function from the Flask.templating package. render_template is used to generate output from the template file layout.html based on the Jinja2 engine.
#### routes folder
The back-end logic of adding, editing, deleting, tracking, and any other function inside the app is in one of the .py files in the routes folder, any of them containing one or more Flask routes.
Here are some of the most important route files in the routes folder:
##### index.py
This file gathers all data there is in the database and also the current or requested year and month. It then uses this data to show information on the dashboard when a GET request is sent to it or returns a search result page when an item is sent to it with a POST request.
##### customers.py and suppliers.py
These files similarly handle customers and suppliers. When a GET request is sent to them, they render a page to show the current list of customers/suppliers. They also handle four types of POST requests for adding, editing, deleting, and the track function.
##### arrivals.py and shipment.py
These files are similar to customers.py and suppliers.py. They handle rendering pages to show the current list of ingredient arrivals/product shipments, and also POST requests for adding, editing, deleting, and the track function. These files ultimately handle half of the inventory functions by adding arrived ingredients and subtracting shipped products. shipment.py also handles AJAX queries for getting in-stock quantity of an item when trying to add a shipment instance to a customer.
##### productions.py
In addition to showing currently entered production instances, adding new ones, and deleting old ones, this file handles the other half of the inventory function by subtracting arrived ingredients as they are used in production instances and adding produced products. It also handles track requests for tracking production instances. production.py also handles AJAX queries for getting ingredients per cent based on the selected recipe for the production instance. Entered production instances.
##### recipes.py
This file handles recipe adding, deleting and tracking. Added recipes are deletable unless they are used to produce something but not editable.
##### types.py
Last but not least, the types.py handles one of the deepest configuration of the database: list of ingredient and production types. This file handles adding, editing, deleting and tracking these types.
### static folder
Bootstrap JavaScript and css, dataTable and d3 chart css and JavaScript, google fonts and icons and images used in the htmls are put in the static folder
