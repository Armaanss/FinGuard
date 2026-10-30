import sqlite3
import pandas as pd

# Connect to database
connection = sqlite3.connect("finguard.db")

# Show all tables
tables = pd.read_sql(
    "SELECT name FROM sqlite_master WHERE type='table'",
    connection
)

print("\n===== DATABASE TABLES =====")
print(tables)


# Show transaction analysis
result = pd.read_sql(
    "SELECT * FROM transaction_analysis",
    connection
)

print("\n===== TRANSACTION ANALYSIS =====")
print(result.to_string(index=False))


# Show risk summary
summary = pd.read_sql("""
    SELECT Risk, COUNT(*) AS Total
    FROM transaction_analysis
    GROUP BY Risk
""", connection)

print("\n===== RISK SUMMARY =====")
print(summary.to_string(index=False))


# Close connection
connection.close()