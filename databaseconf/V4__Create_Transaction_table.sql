CREATE TABLE Transactions(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	txid TEXT,						-- should be encrypted
	fee INTEGER CHECK (fee >= 0) DEFAULT 0,
	status INTEGER NOT NULL,				-- Status from enum
	change_address INTEGER,
	created_at INTEGER,					-- No Date in SQLite -> Epoch-Time
	FOREIGN KEY (change_address) REFERENCES Address(id)
);
