from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import pandas as pd
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize database
def init_db():
    conn = sqlite3.connect('payroll.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            emp_id INTEGER,
            name TEXT,
            basic_salary REAL,
            allowances REAL,
            tax_rate REAL,
            overtime_hours REAL,
            hourly_rate REAL,
            unpaid_leaves INTEGER,
            bonus REAL
        )
    ''')
    conn.commit()
    conn.close()

# Route for login page (admin login)
@app.route('/')
def login():
    return render_template('index.html')

# Route for admin login action
@app.route('/login', methods=['POST'])
def admin_login():
    username = request.form['username']
    password = request.form['password']

    # Simple authentication (hard-coded admin credentials)
    if username == 'admin' and password == 'password':
        session['user'] = 'admin'
        return redirect(url_for('add_employee'))
    else:
        return "Invalid login credentials"

# Route for adding employee (admin page)
@app.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if 'user' in session and session['user'] == 'admin':
        if request.method == 'POST':
            emp_id = request.form['emp_id']
            name = request.form['name']
            basic_salary = request.form['basic_salary']
            allowances = request.form['allowances']
            tax_rate = request.form['tax_rate']
            overtime_hours = request.form['overtime_hours']
            hourly_rate = request.form['hourly_rate']
            unpaid_leaves = request.form['unpaid_leaves']
            bonus = request.form['bonus']

            # Add employee to DB
            conn = sqlite3.connect('payroll.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employees (emp_id, name, basic_salary, allowances, tax_rate, overtime_hours, hourly_rate, unpaid_leaves, bonus)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (emp_id, name, basic_salary, allowances, tax_rate, overtime_hours, hourly_rate, unpaid_leaves, bonus))
            conn.commit()
            conn.close()

            return redirect(url_for('add_employee'))
        return render_template('add_employee.html')
    else:
        return redirect(url_for('login'))

# Route to edit employee
@app.route('/edit_employee/<int:employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    conn = sqlite3.connect('payroll.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        name = request.form['name']
        basic_salary = request.form['basic_salary']
        allowances = request.form['allowances']
        tax_rate = request.form['tax_rate']
        overtime_hours = request.form['overtime_hours']
        hourly_rate = request.form['hourly_rate']
        unpaid_leaves = request.form['unpaid_leaves']
        bonus = request.form['bonus']
        
        # Update employee information
        cursor.execute('''
            UPDATE employees SET emp_id=?, name=?, basic_salary=?, allowances=?, tax_rate=?, overtime_hours=?, hourly_rate=?, unpaid_leaves=?, bonus=?
            WHERE id=?
        ''', (emp_id, name, basic_salary, allowances, tax_rate, overtime_hours, hourly_rate, unpaid_leaves, bonus, employee_id))
        conn.commit()
        conn.close()
        return redirect(url_for('view_records'))

    # Fetch employee data for editing
    cursor.execute('SELECT * FROM employees WHERE id=?', (employee_id,))
    employee = cursor.fetchone()
    conn.close()
    return render_template('edit_employee.html', employee=employee)

# Route for employee view (view records)
@app.route('/view_records')
def view_records():
    conn = sqlite3.connect('payroll.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM employees')
    records = cursor.fetchall()
    conn.close()

    return render_template('view_records.html', records=records)

# Route to export employee data to Excel
@app.route('/export_excel')
def export_excel():
    conn = sqlite3.connect('payroll.db')
    df = pd.read_sql_query('SELECT * FROM employees', conn)
    conn.close()

    excel_file = os.path.join(os.getcwd(), 'payroll_data.xlsx')
    df.to_excel(excel_file, index=False)

    return send_file(excel_file, as_attachment=True)

# Route for dashboard
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('payroll.db')
    df = pd.read_sql_query('SELECT * FROM employees', conn)
    conn.close()
    
    total_employees = len(df)
    total_salary = df['basic_salary'].sum() if not df['basic_salary'].isnull().all() else 0
    total_allowances = df['allowances'].sum() if not df['allowances'].isnull().all() else 0
    total_bonus = df['bonus'].sum() if not df['bonus'].isnull().all() else 0

    return render_template('dashboard.html', total_employees=total_employees, total_salary=total_salary, total_allowances=total_allowances, total_bonus=total_bonus)

# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
