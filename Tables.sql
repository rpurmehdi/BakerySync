CREATE TABLE Sources (
	source_id INTEGER PRIMARY KEY AUTOINCREMENT,
	source_name TEXT NOT NULL UNIQUE,
	source_contact_person TEXT,
	contact_information TEXT,
	source_type TEXT,
	source_location TEXT,
	source_description TEXT
);

CREATE TABLE Destinations (
	destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
	destination_name TEXT NOT NULL UNIQUE,
	destination_contact_person TEXT,
	contact_information TEXT,
	destination_type TEXT,
	destination_location TEXT,
	destination_description TEXT
);

CREATE TABLE RawMaterialTypes (
	material_id INTEGER PRIMARY KEY AUTOINCREMENT,
	material_name TEXT NOT NULL UNIQUE
);

CREATE TABLE ProductionTypes (
	production_id INTEGER PRIMARY KEY AUTOINCREMENT,
	production_name TEXT NOT NULL UNIQUE
);

CREATE TABLE RawMaterialArrival (
	arrival_id INTEGER PRIMARY KEY AUTOINCREMENT,
	material_id INTEGER NOT NULL,
	arrival_time DATETIME NOT NULL,
	source_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id),
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

CREATE TABLE Recipes (
    recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_name TEXT NOT NULL UNIQUE,
    recipe_description TEXT
);

CREATE TABLE RecipeRawMaterialtypes (
    recipe_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity_percent REAL NOT NULL,
    PRIMARY KEY (recipe_id, material_id),
    FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id),
    FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
);

CREATE TABLE Production (
	batch_id INTEGER PRIMARY KEY AUTOINCREMENT,
	print_batch TEXT NOT NULL UNIQUE,
	production_id INTEGER NOT NULL,
	production_time DATETIME NOT NULL,
	recipe_id INTEGER NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id),
	FOREIGN KEY (recipe_id) REFERENCES Recipes (recipe_id)
);

CREATE TABLE ProductionRawMaterialArrivals (
	batch_id INTEGER NOT NULL,
	arrival_id INTEGER NOT NULL,
	FOREIGN KEY (batch_id) REFERENCES Production (batch_id),
	FOREIGN KEY (arrival_id) REFERENCES RawMaterialArrival (arrival_id)
);

CREATE TABLE ProductionShipping (
	shipping_id INTEGER PRIMARY KEY AUTOINCREMENT,
	batch_id INTEGER NOT NULL,
	production_id INTEGER NOT NULL,
	destination_id INTEGER NOT NULL,
	shipping_date DATETIME NOT NULL,
	quantity REAL NOT NULL,
	FOREIGN KEY (batch_id) REFERENCES Production (batch_id),
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id),
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