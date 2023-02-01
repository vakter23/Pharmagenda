import sqlite3

conn = sqlite3.connect('pharmagenda.db',check_same_thread=False)
conn.row_factory = sqlite3.Row

cur = conn.cursor()

cur.executescript("""
    CREATE TABLE IF NOT EXISTS 'user' (
	'idUser'	INTEGER NOT NULL UNIQUE,
	'name'	TEXT,
	'surname'	TEXT,
	idCompany INTEGER,
	PRIMARY KEY('idUser' AUTOINCREMENT),
	FOREIGN KEY('idCompany') REFERENCES 'company'('idCompany')
);
CREATE TABLE IF NOT EXISTS 'company' (
	'idCompany'	INTEGER NOT NULL,
	'company_name'	TEXT,
	'company_address'	TEXT,
	'idUser'	INTEGER,
	PRIMARY KEY('idCompany' AUTOINCREMENT),
	FOREIGN KEY('idUser') REFERENCES 'user'('idUser')
);
CREATE TABLE IF NOT EXISTS 'employee' (
	'idEmployee'	INTEGER NOT NULL,
	'employee_name'	TEXT,
	'employee_surname'	TEXT,
	'color'	TEXT,
	'idCompany'	INTEGER,
	PRIMARY KEY('idEmployee' AUTOINCREMENT),
	FOREIGN KEY('idCompany') REFERENCES 'company'('idCompany')
);
CREATE TABLE IF NOT EXISTS 'workDay' (
	'idWorkDay'	INTEGER NOT NULL,
	'idCompany'	INTEGER,
	'idEmployee'	INTEGER,
	'start_date'	TEXT,
	'end_date'	TEXT,
	PRIMARY KEY('idWorkDay' AUTOINCREMENT),
	FOREIGN KEY('idCompany') REFERENCES 'company'('idCompany')
);

    """)
