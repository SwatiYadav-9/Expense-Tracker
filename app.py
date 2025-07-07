from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Initialize DB
def init_db():
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            description TEXT,
            date TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY,
            monthly_salary REAL
        )''')
        conn.commit()

init_db()

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/add_expense', methods=['POST'])
def add_expense():
    data = request.json
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
                       (data['amount'], data['category'], data['description'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    return jsonify({'status': 'Expense added!'})

@app.route('/get_expenses', methods=['GET'])
def get_expenses():
    category = request.args.get('category', 'All')
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        if category == "All":
            cursor.execute("SELECT * FROM expenses ORDER BY id DESC")
        else:
            cursor.execute("SELECT * FROM expenses WHERE lower(category) = ? ORDER BY id DESC", (category.lower(),))
        rows = cursor.fetchall()
    return jsonify(rows)

@app.route('/delete_expense/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        conn.commit()
    return jsonify({'status': 'Deleted'})

@app.route('/save_salary', methods=['POST'])
def save_salary():
    salary = request.json['salary']
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO user_profile (id, monthly_salary) VALUES (1, ?)", (salary,))
        conn.commit()
    return jsonify({'status': 'Salary saved!'})

@app.route('/get_recommendations', methods=['GET'])
def get_recommendations():
    with sqlite3.connect("expenses.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT monthly_salary FROM user_profile WHERE id = 1")
        result = cursor.fetchone()
        if not result or result[0] is None:
            return jsonify({"status": "Please set salary first", "recommendations": []})
        salary = result[0]

        cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE strftime('%Y-%m', date) = ? GROUP BY lower(category)",
                       (datetime.now().strftime("%Y-%m"),))
        rows = cursor.fetchall()

    # Simple recommendations
    rules = {
        "food": 0.15,
        "rent": 0.30,
        "travelling": 0.10,
        "others": 0.05,
        "electricity": 0.03,
        "grocery": 0.12,
        "bill": 0.08
    }

    total = 0
    recs = []
    for cat, amt in rows:
        total += amt
        if cat.lower() in rules and (amt / salary) > rules[cat.lower()]:
            recs.append(f"{cat.capitalize()} exceeds recommended threshold.")

    saved = salary - total
    if saved < 0.1 * salary:
        recs.append(f"Try to save more! You saved only ₹{saved:.2f}.")
    else:
        recs.append(f"Good! You saved ₹{saved:.2f} this month.")

    return jsonify({"status": "ok", "recommendations": recs})

if __name__ == '__main__':
    app.run(debug=True)
