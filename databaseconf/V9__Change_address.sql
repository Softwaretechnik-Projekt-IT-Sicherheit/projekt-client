DROP TABLE Address;
CREATE TABLE Address(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	address TEXT NOT NULL,				-- Address 
	prkey TEXT NOT NULL,				-- Key(32 Byte)
	balance TEXT,		                 
	updated_at INTEGER,				-- no Datetime-Type in SQLite -> Use of Epoch time
	refund_address INTEGER DEFAULT 0,		-- no Boolean in SQLite -> 0 = false, 1 = true
	wallet INTEGER NOT NULL,
	FOREIGN KEY (wallet) REFERENCES Wallet(id)
);