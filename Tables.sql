CREATE TABLE Sources (
	source_id INTEGER PRIMARY KEY AUTOINCREMENT,
	source_name TEXT NOT NULL UNIQUE,
	source_contact_person TEXT, -- The name of a contact person at the source
	contact_information TEXT, -- Contact details for the source
	source_type TEXT, -- Categorize sources based on type
	source_location TEXT, -- Physical location or origin of the source
	source_description TEXT -- Additional information or notes about the source
);

CREATE TABLE Destinations (
	destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
	destination_name TEXT NOT NULL UNIQUE,
	destination_contact_person TEXT, -- The name of a contact person at the destination
	contact_information TEXT, -- Contact details for the destination
	destination_type TEXT, -- Categorize destinations based on type
	destination_location TEXT, -- Physical location or destination of materials/products
	destination_description TEXT -- Additional information or notes about the destination
);

CREATE TABLE RawMaterialTypes (
	material_id INTEGER PRIMARY KEY AUTOINCREMENT,
	material_name TEXT NOT NULL UNIQUE
	-- Add more attributes as needed
);

CREATE TABLE RawMaterialArrival (
	arrival_id INTEGER PRIMARY KEY AUTOINCREMENT,
	material_id INTEGER NOT NULL,
	arrival_time DATETIME NOT NULL,
	source_id INTEGER NOT NULL, -- Source of the materials (e.g., supplier name or production process).
	quantity REAL NOT NULL,
	FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
	FOREIGN KEY (source_id) REFERENCES Sources (source_id)
);

CREATE TABLE RawMaterialUsage (
	usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
	arrival_id INTEGER NOT NULL,
	material_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	batch_id INTEGER NOT NULL,
	FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id),
	FOREIGN KEY (arrival_id) REFERENCES RawMaterialArrival (arrival_id)
);

CREATE TABLE ProductionTypes (
	production_id INTEGER PRIMARY KEY AUTOINCREMENT,
	production_name TEXT NOT NULL UNIQUE
	-- Add more attributes as needed
);

CREATE TABLE Production (
	batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
	print_batch TEXT NOT NULL UNIQUE,
	production_id INTEGER NOT NULL,
	production_time DATETIME NOT NULL,
	recipe_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id)
	FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id)
);

CREATE TABLE ProductionShipping (
	shipping_id INTEGER PRIMARY KEY AUTOINCREMENT,
	batch_id INTEGER NOT NULL,
	production_id INTEGER NOT NULL,
	destination_id INTEGER NOT NULL, -- Destination of the materials (e.g., buyer name or production process).
	shipping_date DATETIME NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (batch_id) REFERENCES Production (batch_id)
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id)
	FOREIGN KEY (destination_id) REFERENCES Destinations (destination_id)
);

CREATE TABLE InStockRawMaterials (
	arrival_id INTEGER PRIMARY KEY,
	material_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (arrival_id) REFERENCES RawMaterialArrival (arrival_id),
	FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
);

CREATE TABLE InStockProducts (
	batch_id INTEGER PRIMARY KEY,
	production_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (batch_id) REFERENCES Production (batch_id),
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id)	
);

CREATE TABLE Recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL UNIQUE,
    recipe_description TEXT, -- Description of the recipe
);

-- Junction Table to Represent Many-to-Many Relationship between Recipes and RawMaterials
CREATE TABLE RecipeRawMaterials (
    recipe_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity_percent REAL NOT NULL,
    PRIMARY KEY (recipe_id, material_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id),
    FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
);