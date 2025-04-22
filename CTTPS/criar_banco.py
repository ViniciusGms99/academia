import sqlite3

conn = sqlite3.connect('banco.db')
cursor = conn.cursor()

# Tabela de usuários
cursor.execute('''
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL,
    senha TEXT NOT NULL
)
''')

# Tabela de alunos
cursor.execute('''
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    data_nascimento TEXT,
    data_inscricao TEXT,
    mensalidade_paga INTEGER DEFAULT 0,
    ativo INTEGER DEFAULT 1,
    observacoes TEXT
)
''')

# Verifica e adiciona colunas na tabela alunos
cursor.execute("PRAGMA table_info(alunos)")
colunas_alunos = [col[1] for col in cursor.fetchall()]

# Adiciona colunas faltantes dinamicamente
colunas_faltantes = {
    'modalidade': 'TEXT',
    'telefone': 'TEXT',
    'sexo': 'TEXT'
}

for coluna, tipo in colunas_faltantes.items():
    if coluna not in colunas_alunos:
        cursor.execute(f"ALTER TABLE alunos ADD COLUMN {coluna} {tipo}")
        print(f"Coluna '{coluna}' adicionada à tabela 'alunos'.")

# Tabela de eventos
cursor.execute('''
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    tipo TEXT NOT NULL,
    data TEXT NOT NULL
)
''')

# Verifica e adiciona a coluna 'observacoes' na tabela eventos
cursor.execute("PRAGMA table_info(eventos)")
colunas_eventos = [col[1] for col in cursor.fetchall()]
if 'observacoes' not in colunas_eventos:
    cursor.execute("ALTER TABLE eventos ADD COLUMN observacoes TEXT")
    print("Coluna 'observacoes' adicionada à tabela 'eventos'.")

# Tabela de financeiro
cursor.execute('''
CREATE TABLE IF NOT EXISTS financeiro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL,
    tipo TEXT NOT NULL CHECK(tipo IN ('entrada', 'saida')),
    valor REAL NOT NULL,
    data TEXT NOT NULL
)
''')

# Tabela de grade
cursor.execute('''
CREATE TABLE IF NOT EXISTS grade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    modalidade TEXT NOT NULL,
    professor TEXT NOT NULL,
    horario TEXT NOT NULL,
    dia_semana TEXT NOT NULL
)
''')

# Tabela de participações
cursor.execute('''
CREATE TABLE IF NOT EXISTS participacoes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    evento_id INTEGER,
    resultado TEXT,
    FOREIGN KEY (aluno_id) REFERENCES alunos(id),
    FOREIGN KEY (evento_id) REFERENCES eventos(id)
)
''')

conn.commit()
conn.close()

print("Banco de dados criado/atualizado com sucesso!")
