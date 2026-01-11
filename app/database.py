import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT,
    prediction TEXT,
    confidence REAL,
    timestamp TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    email TEXT,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    email TEXT,
    subject TEXT,
    body TEXT,
    status TEXT DEFAULT 'new',
    timestamp TEXT
)
""")

cursor.execute("""
    ALTER TABLE messages ADD COLUMN status TEXT DEFAULT 'new'
""")

conn.commit()
conn.close()

print("Tables created")
