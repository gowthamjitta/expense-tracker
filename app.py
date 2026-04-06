from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Create database
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL,
            category TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()   # ✅ IMPORTANT FIX

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    # Add expense
    if request.method == 'POST':
        amount = request.form['amount']
        category = request.form['category']
        date = request.form['date']

        c.execute(
            "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
            (amount, category, date)
        )
        conn.commit()
        return redirect('/')

    # Get all expenses
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()

    # Monthly total
    month = datetime.now().strftime("%Y-%m")
    c.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (month + "%",))
    monthly_total = c.fetchone()[0] or 0

    # Yearly total
    year = datetime.now().strftime("%Y")
    c.execute("SELECT SUM(amount) FROM expenses WHERE date LIKE ?", (year + "%",))
    yearly_total = c.fetchone()[0] or 0

    # Graph data
    c.execute("SELECT date, amount FROM expenses")
    graph_data = c.fetchall()

    dates = [row[0] for row in graph_data]
    amounts = [row[1] for row in graph_data]

    conn.close()

    return render_template(
        "index.html",
        data=data,
        monthly_total=monthly_total,
        yearly_total=yearly_total,
        dates=dates,
        amounts=amounts
    )

# Delete expense
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# Run app (Render compatible)
import os

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 10000))  # IMPORTANT
    app.run(host="0.0.0.0", port=port)