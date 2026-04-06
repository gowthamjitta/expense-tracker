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
    init_db()

    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()

    # Add expense
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        category = request.form.get('category', '')
        date = request.form.get('date', '')

        if amount > 0 and category and date:
            c.execute(
                "INSERT INTO expenses (amount, category, date) VALUES (?, ?, ?)",
                (amount, category, date)
            )
            conn.commit()
        return redirect('/')

    # Fetch all data
    c.execute("SELECT * FROM expenses")
    data = c.fetchall()

    # Today's total
    today = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT SUM(amount) FROM expenses WHERE date = ?", (today,))
    today_total = c.fetchone()[0] or 0

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

    dates = [str(row[0]) for row in graph_data]
    amounts = [float(row[1]) for row in graph_data]

    conn.close()

    return render_template(
        "index.html",
        data=data,
        today_total=today_total,
        monthly_total=monthly_total,
        yearly_total=yearly_total,
        dates=dates,
        amounts=amounts
    )

# Delete
@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/')

# Run
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)