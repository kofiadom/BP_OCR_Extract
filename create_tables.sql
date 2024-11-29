CREATE TABLE bp_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    systolic INTEGER,
    diastolic INTEGER,
    pulse INTEGER,
    risk_score REAL,
    measurement_time DATETIME
);

CREATE TABLE reminders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT
);

CREATE TABLE clinicians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    specialty TEXT,
    contact TEXT
);

-- Example Clinician Data
INSERT INTO clinicians (name, specialty, contact) VALUES 
("Dr. Kwame Mensah", "Cardiologist", "0241234567"),
("Dr. Ama Boateng", "General Practitioner", "0269876543");
