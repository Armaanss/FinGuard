import sqlite3
import pandas as pd

# Read CSV file
data = pd.read_csv("transactions.csv")

# Connect to SQLite database
connection = sqlite3.connect("finguard.db")

# Insert CSV data into transactions table
data.to_sql(
    "transactions",
    connection,
    if_exists="replace",
    index=False
)

# Save changes
connection.commit()

# Check the data
print("\n===== DATA STORED IN DATABASE =====")

result = pd.read_sql(
    "SELECT * FROM transactions",
    connection
)

print(result)

# Close connection
connection.close()

print("\nTransactions successfully stored in FinGuard database!")