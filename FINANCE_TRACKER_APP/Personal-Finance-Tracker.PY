
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize the database
def init_db():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Add a transaction to the database
def add_transaction(description, amount, category, date):
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transactions (description, amount, category, date)
        VALUES (?, ?, ?, ?)
    ''', (description, amount, category, date))
    conn.commit()
    conn.close()

# Retrieve all transactions
def get_transactions():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM transactions ORDER BY date DESC')
    transactions = cursor.fetchall()
    conn.close()
    return transactions

# Calculate summary
def calculate_summary():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount > 0')
    income = cursor.fetchone()[0] or 0
    cursor.execute('SELECT SUM(amount) FROM transactions WHERE amount < 0')
    expenses = cursor.fetchone()[0] or 0
    conn.close()
    balance = income + expenses
    return income, abs(expenses), balance

# Generate category report
def generate_category_report():
    conn = sqlite3.connect('finance_tracker.db')
    cursor = conn.cursor()
    cursor.execute('SELECT category, SUM(amount) FROM transactions WHERE amount < 0 GROUP BY category')
    data = cursor.fetchall()
    conn.close()
    if data:
        categories = [row[0] for row in data]
        amounts = [abs(row[1]) for row in data]
        plt.figure(figsize=(6,6))
        plt.pie(amounts, labels=categories, autopct='%1.1f%%')
        plt.title('Expenses by Category')
        plt.show()
    else:
        messagebox.showinfo("No Data", "No expense data available to generate report.")

# GUI Application
class FinanceTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("600x600")
        self.create_widgets()
        self.refresh_transactions()

    def create_widgets(self):
        # Transaction Entry Frame
        entry_frame = ttk.LabelFrame(self.root, text="Add Transaction")
        entry_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(entry_frame, text="Description:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.desc_entry = ttk.Entry(entry_frame, width=30)
        self.desc_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Amount:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.amount_entry = ttk.Entry(entry_frame, width=30)
        self.amount_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Category:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.category_entry = ttk.Entry(entry_frame, width=30)
        self.category_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(entry_frame, text="Date (YYYY-MM-DD):").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = ttk.Entry(entry_frame, width=30)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        add_income_btn = ttk.Button(entry_frame, text="Add Income", command=self.add_income)
        add_income_btn.grid(row=4, column=0, padx=5, pady=10)

        add_expense_btn = ttk.Button(entry_frame, text="Add Expense", command=self.add_expense)
        add_expense_btn.grid(row=4, column=1, padx=5, pady=10)

        # Transactions List Frame
        list_frame = ttk.LabelFrame(self.root, text="Transactions")
        list_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Description", "Amount", "Category", "Date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Summary Frame
        summary_frame = ttk.LabelFrame(self.root, text="Summary")
        summary_frame.pack(fill="x", padx=10, pady=10)

        self.income_var = tk.StringVar()
        self.expense_var = tk.StringVar()
        self.balance_var = tk.StringVar()

        ttk.Label(summary_frame, text="Total Income:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.income_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(summary_frame, text="Total Expenses:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.expense_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(summary_frame, text="Balance:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        ttk.Label(summary_frame, textvariable=self.balance_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Report Button
        report_btn = ttk.Button(self.root, text="Generate Category Report", command=generate_category_report)
        report_btn.pack(pady=10)

    def add_income(self):
        self.add_transaction_entry(is_income=True)

    def add_expense(self):
        self.add_transaction_entry(is_income=False)

    def add_transaction_entry(self, is_income):
        description = self.desc_entry.get().strip()
        amount = self.amount_entry.get().strip()
        category = self.category_entry.get().strip()
        date = self.date_entry.get().strip()

        if not description or not amount or not category or not date:
            messagebox.showerror("Input Error", "All fields are required.")
            return

        try:
            amount = float(amount)
            if not is_income:
                amount = -abs(amount)
            else:
                amount = abs(amount)
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number.")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.")
            return

        add_transaction(description, amount, category, date)
        messagebox.showinfo("Success", "Transaction added successfully.")
        self.clear_entries()
        self.refresh_transactions()

    def clear_entries(self):
        self.desc_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def refresh_transactions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        transactions = get_transactions()
        for txn in transactions:
            self.tree.insert("", tk.END, values=txn)
        income, expenses, balance = calculate_summary()
        self.income_var.set(f"₹{income:.2f}")
        self.expense_var.set(f"₹{expenses:.2f}")
        self.balance_var.set(f"₹{balance:.2f}")

if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FinanceTrackerApp(root)
    root.mainloop()
