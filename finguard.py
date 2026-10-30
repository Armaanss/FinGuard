import pandas as pd
import sqlite3

# ==========================================
# 1. READ TRANSACTION DATA
# ==========================================

data = pd.read_csv("transactions.csv")

print("\n===== ORIGINAL DATA =====")
print(data)


# ==========================================
# 2. DATA CLEANING
# ==========================================

data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
data["Amount"] = pd.to_numeric(data["Amount"], errors="coerce")

# Convert Time into datetime time format
data["Time"] = pd.to_datetime(
    data["Time"], format="%H:%M", errors="coerce"
).dt.time

# Remove rows with missing important values
data = data.dropna(
    subset=["TransactionID", "Date", "Time", "Category", "Amount",
            "Location", "Merchant"]
)

# Remove exact duplicate rows only
data = data.drop_duplicates()

# Keep only positive transactions
data = data[data["Amount"] > 0]

# Create combined DateTime column
data["DateTime"] = pd.to_datetime(
    data["Date"].dt.strftime("%Y-%m-%d") + " " +
    data["Time"].astype(str)
)

print("\n===== CLEANED DATA =====")
print(data)


# ==========================================
# 3. FRAUD / ANOMALY DETECTION
# ==========================================

def analyze_transaction(index, row, data):

    risk_score = 0
    reasons = []
    score_breakdown = []

    # --------------------------------------
    # RULE 1: Very High Transaction Amount
    # --------------------------------------

    if row["Amount"] > 50000:
        risk_score += 30
        reasons.append("Very high transaction amount")
        score_breakdown.append("Very high transaction amount: +30")


    # --------------------------------------
    # RULE 2: Unusual Travel Expense
    # --------------------------------------

    if row["Category"] == "Travel" and row["Amount"] > 30000:
        risk_score += 25
        reasons.append("Unusually high travel expense")
        score_breakdown.append("Unusually high travel expense: +25")


    # --------------------------------------
    # RULE 3: Transaction at Unusual Time
    # --------------------------------------

    hour = row["DateTime"].hour

    if hour < 6 or hour >= 23:
        risk_score += 20
        reasons.append("Transaction made at unusual time")
        score_breakdown.append("Transaction made at unusual time: +20")


    # --------------------------------------
    # RULE 4: Possible Duplicate Transaction
    # --------------------------------------

    duplicate_rows = data[
        (data["Date"] == row["Date"]) &
        (data["Category"] == row["Category"]) &
        (data["Amount"] == row["Amount"]) &
        (data["Location"] == row["Location"]) &
        (data["Merchant"] == row["Merchant"])
    ]

    if len(duplicate_rows) > 1:
        risk_score += 25
        reasons.append("Possible duplicate transaction")
        score_breakdown.append("Possible duplicate transaction: +25")


    # --------------------------------------
    # RULE 5: Rapid Repeated Transactions
    # --------------------------------------

    nearby = data[
        (data["Merchant"] == row["Merchant"]) &
        (data["Location"] == row["Location"]) &
        (data["DateTime"] != row["DateTime"])
    ].copy()

    if not nearby.empty:

        time_difference = (
            abs(nearby["DateTime"] - row["DateTime"])
            .dt.total_seconds() / 60
        )

        if (time_difference <= 10).any():
            risk_score += 10
            reasons.append("Multiple transactions within 10 minutes")
            score_breakdown.append(
                "Multiple transactions within 10 minutes: +10"
            )


    # --------------------------------------
    # RULE 6: Repeated Merchant Spending
    # --------------------------------------

    merchant_count = len(
        data[
            (data["Merchant"] == row["Merchant"]) &
            (data["Date"] == row["Date"])
        ]
    )

    if merchant_count >= 2:
        risk_score += 5
        reasons.append("Repeated spending at same merchant")
        score_breakdown.append(
            "Repeated spending at same merchant: +5"
        )


    # --------------------------------------
    # RULE 7: Category Spending Anomaly
    # --------------------------------------

    category_data = data[
        data["Category"] == row["Category"]
    ]

    category_median = category_data["Amount"].median()

    if (
        len(category_data) >= 3 and
        row["Amount"] > category_median * 3
    ):
        risk_score += 15
        reasons.append("Unusually high spending for category")
        score_breakdown.append(
            "Unusually high spending for category: +15"
        )


    # ======================================
    # RISK LEVEL
    # ======================================

    if risk_score >= 60:
        risk = "HIGH"

    elif risk_score >= 30:
        risk = "MEDIUM"

    else:
        risk = "LOW"


    return risk_score, risk, reasons, score_breakdown


# ==========================================
# 4. APPLY ANALYSIS
# ==========================================

results = []

for index, row in data.iterrows():

    score, risk, reasons, score_breakdown = analyze_transaction(
        index, row, data
    )

    results.append({
        "TransactionID": row["TransactionID"],
        "Date": row["Date"].date(),
        "Time": row["Time"],
        "Category": row["Category"],
        "Amount": row["Amount"],
        "Location": row["Location"],
        "Merchant": row["Merchant"],
        "RiskScore": score,
        "Risk": risk,
        "Reason": ", ".join(reasons) if reasons else "Normal transaction",
        "ScoreBreakdown": ", ".join(score_breakdown) if score_breakdown else "No risk points"
    })


# ==========================================
# 5. CREATE RESULT DATAFRAME
# ==========================================

result_data = pd.DataFrame(results)

# ==========================================
# SAVE RESULTS TO SQLITE DATABASE
# ==========================================

connection = sqlite3.connect("finguard.db")

result_data.to_sql(
    "transaction_analysis",
    connection,
    if_exists="replace",
    index=False
)

connection.commit()
connection.close()

print("\nAnalysis results successfully stored in SQLite database!")

# ==========================================
# 6. DISPLAY RESULTS
# ==========================================

print("\n===== FINGUARD ANALYSIS RESULTS =====")

print(
    result_data[
        [
            "TransactionID",
            "Category",
            "Amount",
            "Location",
            "Merchant",
            "RiskScore",
            "Risk",
            "Reason"
        ]
    ].to_string(index=False)
)


# ==========================================
# 7. SHOW SUSPICIOUS TRANSACTIONS
# ==========================================

suspicious = result_data[
    result_data["Risk"] != "LOW"
]

print("\n===== SUSPICIOUS TRANSACTIONS =====")

if suspicious.empty:
    print("No suspicious transactions found.")

else:
    print(
        suspicious[
            [
                "TransactionID",
                "Amount",
                "RiskScore",
                "Risk",
                "Reason"
            ]
        ].to_string(index=False)
    )


# ==========================================
# 8. SUMMARY
# ==========================================

total_transactions = len(result_data)
total_expenses = result_data["Amount"].sum()

high_risk = len(result_data[result_data["Risk"] == "HIGH"])
medium_risk = len(result_data[result_data["Risk"] == "MEDIUM"])
low_risk = len(result_data[result_data["Risk"] == "LOW"])

print("\n===== FINGUARD SUMMARY =====")

print("Total Transactions :", total_transactions)
print("Total Expenses     : ₹", total_expenses)
print("High Risk          :", high_risk)
print("Medium Risk        :", medium_risk)
print("Low Risk           :", low_risk)