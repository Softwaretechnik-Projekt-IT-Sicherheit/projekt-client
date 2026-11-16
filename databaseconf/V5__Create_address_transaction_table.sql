CREATE TABLE Address_Transaction(	-- Need becaus one aransaction can have multiple adresses and addresses acn have multiple transactions
	add_id INTEGER NOT NULL,
	trans_id INTEGER NOT NULL,
	PRIMARY KEY(add_id, trans_id),
	FOREIGN KEY (add_id) REFERENCES Address(id),
	FOREIGN KEY (trans_id) REFERENCES Transactions(id)
);
