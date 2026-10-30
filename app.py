from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = "finguard_secret_key"

# Connect to database
def get_database():
    connection = sqlite3.connect("finguard.db")
    connection.row_factory = sqlite3.Row
    return connection


# Dashboard
@app.route("/")
def home():

    if "user_id" not in session:
        return redirect(url_for("login"))
    
    connection = get_database()

    transactions = connection.execute(
        "SELECT * FROM transaction_analysis"
    ).fetchall()

    summary = connection.execute("""
        SELECT Risk, COUNT(*) AS Total
        FROM transaction_analysis
        GROUP BY Risk
    """).fetchall()

    category_summary = connection.execute("""
        SELECT Category, COUNT(*) AS Total
        FROM transaction_analysis
        GROUP BY Category
    """).fetchall()

    connection.close()

    risk_counts = {
        "HIGH": 0,
        "MEDIUM": 0,
        "LOW": 0
    }

    for row in summary:
        risk_counts[row["Risk"]] = row["Total"]

    categories = [row["Category"] for row in category_summary]
    category_counts = [row["Total"] for row in category_summary]

    return render_template(
        "index.html",
        transactions=transactions,
        total=len(transactions),
        high=risk_counts["HIGH"],
        medium=risk_counts["MEDIUM"],
        low=risk_counts["LOW"],
        categories=categories,
        category_counts=category_counts
    )

@app.route("/transaction/<transaction_id>")
def transaction_details(transaction_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    connection = get_database()

    transaction = connection.execute(
        """
        SELECT *
        FROM transaction_analysis
        WHERE TransactionID = ?
        """,
        (transaction_id,)
    ).fetchone()

    connection.close()

    if transaction is None:
        return "Transaction not found", 404

    return render_template(
        "transaction_details.html",
        transaction=transaction
    )

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = get_database()

        user = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

        connection.close()

        if user and check_password_hash(user["password"], password):

            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect(url_for("home"))

        return render_template(
            "login.html",
            error="Invalid username or password"
        )

    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("login"))

@app.route("/admin")
def admin():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "ADMIN":
        return "Access Denied: Admins only", 403

    connection = get_database()

    users = connection.execute(
        "SELECT id, username, role FROM users"
    ).fetchall()

    total_users = len(users)

    total_admins = connection.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'ADMIN'"
    ).fetchone()[0]

    total_normal_users = connection.execute(
        "SELECT COUNT(*) FROM users WHERE role = 'USER'"
    ).fetchone()[0]

    connection.close()

    return render_template(
        "admin.html",
        users=users,
        total_users=total_users,
        total_admins=total_admins,
        total_normal_users=total_normal_users
    )

@app.route("/create-user", methods=["POST"])
def create_user():

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "ADMIN":
        return "Access Denied: Admins only", 403

    username = request.form["username"]
    password = request.form["password"]
    role = request.form["role"]

    password_hash = generate_password_hash(password)

    connection = get_database()

    try:
        connection.execute(
            """
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password_hash, role)
        )

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()
        return "Username already exists", 400

    connection.close()

    return redirect(url_for("admin"))

@app.route("/delete-user/<int:user_id>", methods=["POST"])
def delete_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    if session["role"] != "ADMIN":
        return "Access Denied: Admins only", 403

    # Prevent deleting your own account
    if user_id == session["user_id"]:
        return "You cannot delete your own account.", 400

    connection = get_database()

    # Check whether the user exists
    user = connection.execute(
        "SELECT id FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()

    if user is None:
        connection.close()
        return "User not found", 404

    # Delete the selected user
    connection.execute(
        "DELETE FROM users WHERE id = ?",
        (user_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("admin"))

if __name__ == "__main__":
    app.run(debug=True)