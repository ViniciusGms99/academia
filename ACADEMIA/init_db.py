import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Tabela de usuários (admins do sistema)
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Tabela de alunos
cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    birthdate TEXT NOT NULL,
    enrollment_date TEXT NOT NULL,
    age INTEGER NOT NULL,
    bolsa_atleta INTEGER NOT NULL,
    mensalidade_pago INTEGER NOT NULL
)
''')

conn.commit()
conn.close()
print("Banco de dados inicializado com sucesso!")
