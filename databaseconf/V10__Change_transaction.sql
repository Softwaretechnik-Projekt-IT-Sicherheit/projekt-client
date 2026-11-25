DROP TABLE Transactions;
CREATE TABLE Transactions(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	txid TEXT,						-- should be encrypted
	fee TEXT,
	status INTEGER NOT NULL,				-- Status from enum
	change_address INTEGER,
	created_at INTEGER,					-- No Date in SQLite -> Epoch-Time
	FOREIGN KEY (change_address) REFERENCES Address(id)
);
