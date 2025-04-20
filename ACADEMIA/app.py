from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'segredo-super-seguro'

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('login'))

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        return render_template('login.html', error='Login inválido!')
    return render_template('login.html')

# ---------------- REGISTRO ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('register.html', error='Email já cadastrado!')
        conn.close()
        return redirect(url_for('login'))
    return render_template('register.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    students = conn.execute('SELECT * FROM students').fetchall()
    conn.close()
    return render_template('dashboard.html', students=students)

# ---------------- NOVO ALUNO ----------------
@app.route('/new-student', methods=['GET', 'POST'])
def new_student():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        birthdate = request.form['birthdate']
        bolsa_atleta = 1 if 'bolsa_atleta' in request.form else 0
        mensalidade_pago = 1 if 'mensalidade_pago' in request.form else 0

        birth_date = datetime.strptime(birthdate, '%Y-%m-%d')
        today = datetime.today()
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        enrollment_date = today.strftime('%Y-%m-%d')

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO students (name, birthdate, enrollment_date, age, bolsa_atleta, mensalidade_pago)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, birthdate, enrollment_date, age, bolsa_atleta, mensalidade_pago))
        conn.commit()
        conn.close()
        return redirect(url_for('dashboard'))

    return render_template('new_student.html')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
