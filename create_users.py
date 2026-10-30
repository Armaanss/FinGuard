import sqlite3
from werkzeug.security import generate_password_hash

connection = sqlite3.connect("finguard.db")

cursor = connection.cursor()

# Create users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
""")

# Create Admin account
admin_password = generate_password_hash("admin123")

cursor.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES (?, ?, ?)
""", ("admin", admin_password, "ADMIN"))


# Create normal User account
user_password = generate_password_hash("user123")

cursor.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES (?, ?, ?)
""", ("user", user_password, "USER"))


connection.commit()
connection.close()

print("Users table created successfully.")
print("Admin account: admin / admin123")
print("User account: user / user123")