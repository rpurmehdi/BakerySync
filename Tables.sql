CREATE TABLE RawMaterialTypes (
    material_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_name TEXT NOT NULL UNIQUE,
    -- Add more attributes as needed
);

CREATE TABLE RawMaterialArrival (
    arrival_id INTEGER PRIMARY KEY AUTOINCREMENT,
    material_id INTEGER NOT NULL,
    arrival_time DATETIME NOT NULL,
    source TEXT, -- Source of the materials (e.g., supplier name or production process).
    quantity REAL NOT NULL,
    FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
);

CREATE TABLE RawMaterialUsage (
    usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
	arrival_id INTEGER NOT NULL,
    material_id INTEGER NOT NULL,
    quantity REAL NOT NULL,
	batch_id INTEGER NOT NULL,
    FOREIGN KEY (material_id) REFERENCES RawMaterialTypes (material_id)
	FOREIGN KEY (arrival_id) REFERENCES RawMaterialArrival (arrival_id)
);

CREATE TABLE ProductionTypes (
    production_id INTEGER PRIMARY KEY AUTOINCREMENT,
    production_name TEXT NOT NULL UNIQUE,
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
    destination TEXT, -- Destination of the materials (e.g., buyer name or production process).
	shipping_date DATETIME NOT NULL,
    quantity REAL NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES Production (batch_id)
	FOREIGN KEY (production_id) REFERENCES ProductionTypes (production_id)
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




