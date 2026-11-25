DROP TABLE Target_Addresses;
CREATE TABLE Target_Addresses(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    trans_id INTEGER NOT NULL,
    address TEXT,                                    -- Target Address of Transaction as String (creating new Adrress object makes no sens, because only Address is known)
    amount TEXT
);