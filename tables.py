import sqlite3

conn = sqlite3.connect("patient_app.db")
cursor = conn.cursor()

with open("create_tables.sql", "r") as f:
    sql_script = f.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()
print("Tables created successfully!")