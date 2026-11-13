CREATE TABLE Address(
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	address VARCHAR(62) NOT NULL,			-- max of 62 Characters possible at beginning without encryption
	prkey CHAR(64) NOT NULL,			-- Key(32 Byte) -> AES -> 32 Bytes + 16 Bytes
	balance INTEGER CHECK(balance >= 0),		-- be shur that no negativ bitcoins are on wallet
	updated_at INTEGER,				-- no Datetime-Type in SQLite -> Use of Epoch time
	refund_address INTEGER DEFAULT 0,		-- no Boolean in SQLite -> 0 = false, 1 = true
	wallet INTEGER NOT NULL,
	FOREIGN KEY (wallet) REFERENCES Wallet(id)
);
