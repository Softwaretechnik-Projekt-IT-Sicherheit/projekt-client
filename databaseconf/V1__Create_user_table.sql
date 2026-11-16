CREATE TABLE User (
	id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,		-- Chooses id by itself
	username VARCHAR(255) NOT NULL UNIQUE,		-- user is Identifier -> must be unique
	password_hash CHAR(32),				-- pland for SHA256
	salt VARCHAR(30) NOT NULL UNIQUE		-- salt should be unique
);
