from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'chave-secreta'

# ========== CONEXÃO COM O BANCO ==========
def get_db_connection():
    conn = sqlite3.connect('banco.db')
    conn.row_factory = sqlite3.Row
    return conn

# ========== FUNÇÕES AUXILIARES ==========
def pegar_proximo_evento():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT nome, data FROM eventos WHERE data >= date('now') ORDER BY data ASC LIMIT 1")
    evento = cursor.fetchone()
    conn.close()
    if evento:
        return {'nome': evento['nome'], 'data': datetime.strptime(evento['data'], '%Y-%m-%d')}
    return None

def contar_alunos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM alunos WHERE ativo = 1")
    total = cursor.fetchone()['total']
    conn.close()
    return total

def calcular_saldo():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(valor) AS total FROM financeiro WHERE tipo = 'entrada'")
    entradas = cursor.fetchone()['total'] or 0
    cursor.execute("SELECT SUM(valor) AS total FROM financeiro WHERE tipo = 'saida'")
    saidas = cursor.fetchone()['total'] or 0
    conn.close()
    return round(entradas - saidas, 2)

def buscar_aulas_do_dia():
    dia_semana = datetime.now().strftime('%A').lower()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT modalidade, horario FROM grade WHERE dia_semana = ?", (dia_semana,))
    aulas = cursor.fetchall()
    conn.close()
    return [{'modalidade': a['modalidade'], 'horario': a['horario']} for a in aulas]

# ========== DASHBOARD ==========
@app.route('/')
def dashboard():
    if 'usuario' not in session:
        return redirect(url_for('login'))

    proximo_evento = pegar_proximo_evento()
    total_alunos = contar_alunos()
    saldo_atual = calcular_saldo()
    aulas_hoje = buscar_aulas_do_dia()

    return render_template('dashboard.html',
                           proximo_evento=proximo_evento,
                           total_alunos=total_alunos,
                           saldo_atual=saldo_atual,
                           aulas_hoje=aulas_hoje)

# ========== LOGIN ==========
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if not usuario or not senha:
            return render_template('login.html', erro='Preencha todos os campos.')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['usuario'] = usuario
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', erro='Usuário ou senha inválidos.')
    return render_template('login.html')

# ========== LOGOUT ==========
@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# ========== REGISTRO ==========
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        if not usuario or not senha:
            return render_template('register.html', erro='Preencha todos os campos.')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except Exception as e:
            return render_template('register.html', erro=f'Erro ao registrar: {e}')
        
    return render_template('register.html')

# ========== EVENTOS ==========
def formatar_eventos(eventos):
    eventos_formatados = []
    for evento in eventos:
        data_br = datetime.strptime(evento['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
        eventos_formatados.append({
            'id': evento['id'],
            'nome': evento['nome'],
            'data': data_br,
            'observacoes': evento['observacoes'],
        })
    return eventos_formatados

@app.route('/eventos')
def eventos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM eventos WHERE tipo = 'campeonato' ORDER BY data ASC")
    campeonatos = formatar_eventos(cursor.fetchall())
    cursor.execute("SELECT * FROM eventos WHERE tipo = 'exame' ORDER BY data ASC")
    exames = formatar_eventos(cursor.fetchall())
    conn.close()
    return render_template('eventos.html', campeonatos=campeonatos, exames=exames)

@app.route('/cadastrar_evento', methods=['POST'])
def cadastrar_evento():
    nome = request.form['nome']
    tipo = request.form['tipo']
    data = request.form['data']
    observacoes = request.form.get('observacoes', '')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO eventos (nome, tipo, data, observacoes) VALUES (?, ?, ?, ?)',
                   (nome, tipo, data, observacoes))
    conn.commit()
    conn.close()
    return redirect(url_for('eventos'))

@app.route('/editar_evento/<int:id>', methods=['GET', 'POST'])
def editar_evento(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        data = request.form['data']
        observacoes = request.form.get('observacoes', '')
        cursor.execute('UPDATE eventos SET nome=?, data=?, observacoes=? WHERE id=?',
                       (nome, data, observacoes, id))
        conn.commit()
        conn.close()
        return redirect(url_for('eventos'))

    cursor.execute('SELECT * FROM eventos WHERE id=?', (id,))
    evento = cursor.fetchone()
    conn.close()

    if evento:
        return render_template('editar_evento.html', evento=evento)
    else:
        return 'Evento não encontrado.'

@app.route('/excluir_evento/<int:id>')
def excluir_evento(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM eventos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('eventos'))

# ========== ALUNOS ==========
@app.route('/alunos')
def alunos():
    nome_filtro = request.args.get('nome', '').strip().lower()

    con = get_db_connection()
    cursor = con.cursor()

    if nome_filtro:
        cursor.execute("SELECT * FROM alunos WHERE LOWER(nome) LIKE ? ORDER BY nome", (f"%{nome_filtro}%",))
    else:
        cursor.execute("SELECT * FROM alunos ORDER BY nome")

    todos = cursor.fetchall()
    con.close()

    ativos = [a for a in todos if a['ativo'] == 1]
    inativos = [a for a in todos if a['ativo'] == 0]

    return render_template('alunos.html', ativos=ativos, inativos=inativos, nome_filtro=nome_filtro)



@app.route('/cadastrar_aluno', methods=['GET', 'POST'])
def cadastrar_aluno():
    if request.method == 'POST':
        nome = request.form.get('nome', '')
        nascimento = request.form.get('nascimento', '')
        telefone = request.form.get('telefone', '')
        modalidade = request.form.get('modalidade', '')
        observacoes = request.form.get('observacoes', '')
        mensalidade_paga = int(request.form.get('mensalidade_paga', 0))
        ativo = int(request.form.get('ativo', 1))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO alunos (nome, data_nascimento, telefone, modalidade, observacoes, mensalidade_paga, ativo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, nascimento, telefone, modalidade, observacoes, mensalidade_paga, ativo))
        conn.commit()
        conn.close()

        return redirect(url_for('alunos'))

    return render_template('cadastrar_aluno.html')

@app.route('/editar_aluno/<int:id>', methods=['GET', 'POST'])
def editar_aluno(id):
    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        nome = request.form['nome']
        nascimento = request.form['nascimento']
        telefone = request.form['telefone']
        modalidade = request.form['modalidade']
        observacoes = request.form.get('observacoes', '')
        sexo = request.form['sexo']
        ativo = int(request.form.get('ativo', 1))

        cursor.execute('''
            UPDATE alunos
            SET nome = ?, data_nascimento = ?, telefone = ?, modalidade = ?, observacoes = ?, sexo = ?, ativo = ?
            WHERE id = ?
        ''', (nome, nascimento, telefone, modalidade, observacoes, sexo, ativo, id))
        conn.commit()
        conn.close()
        return redirect(url_for('alunos'))

    # GET – exibir dados atuais
    cursor.execute('SELECT * FROM alunos WHERE id = ?', (id,))
    aluno = cursor.fetchone()
    conn.close()
    return render_template('editar_aluno.html', aluno=aluno)

@app.route('/deletar_aluno/<int:id>')
def deletar_aluno(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM alunos WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('alunos'))

# ========== EXECUTAR ==========
if __name__ == '__main__':
    app.run(debug=True)