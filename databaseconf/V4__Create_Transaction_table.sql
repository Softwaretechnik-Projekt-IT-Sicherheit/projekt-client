CREATE TABLE Transactions(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	txid TEXT,						-- should be encrypted
	amount INTEGER CHECK (amount >= 0) DEFAULT 0,		-- no unsigned
	fee INTEGER CHECK (amount >= 0) DEFAULT 0,
	change_address TEXT,					-- should be encrypted
	status INTEGER NOT NULL,				-- Status from enum
	created_at INTEGER					-- No Date in SQLite -> Epoch-Time
);
