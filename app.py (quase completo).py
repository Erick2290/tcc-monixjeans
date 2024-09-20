from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Defina uma chave secreta para uso das sessões

# Configurações do banco de dados
db = pymysql.connect(host='localhost', user='root', password='123456', database='testemonix78', autocommit=True)
cursor = db.cursor()

# Função para verificar se o usuário está autenticado
def usuario_autenticado():
    return 'usuario' in session

# Rota para o login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['senha']

        try:
            cursor.execute('SELECT * FROM Usuario WHERE nome=%s AND senha=%s', (username, password))
            user = cursor.fetchone()

            if user:
                session['usuario'] = username
                return jsonify({'success': True})  # Retorna um JSON indicando sucesso
            else:
                return jsonify({'success': False, 'message': 'Usuário ou senha incorretos'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Erro ao acessar o banco de dados: ' + str(e)})
    
    return render_template('login.html')

# Rota para o menu principal (requer autenticação)
@app.route('/')
def menu():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('menu.html')

# Rota para o registro de usuários
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar-senha']

        if senha == confirmar_senha:
            try:
                cursor.execute('INSERT INTO Usuario (cpf, senha, nome) VALUES (%s, %s, %s)', (cpf, senha, nome))
                return jsonify({'status': 'success'})  # Retorna um JSON indicando sucesso
            except Exception as e:
                return jsonify({'status': 'error', 'message': 'Erro ao acessar o banco de dados: ' + str(e)})
        else:
            return jsonify({'status': 'error', 'message': 'As senhas não coincidem'})  # Retorna um JSON indicando erro de senhas
    else:
        return render_template('registro.html')

# Rota para deletar conta
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    usuario = session['usuario']
    try:
        cursor.execute('DELETE FROM Usuario WHERE nome=%s', (usuario,))
        session.pop('usuario', None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao deletar a conta: ' + str(e)})

# Rota para editar conta
@app.route('/edit_account', methods=['POST'])
def edit_account():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    usuario = session['usuario']
    senha_antiga = data['senha_antiga']
    nova_senha = data['nova_senha']
    novo_nome = data['novo_nome']
    novo_cpf = data['novo_cpf']

    try:
        cursor.execute('SELECT * FROM Usuario WHERE nome=%s AND senha=%s', (usuario, senha_antiga))
        user = cursor.fetchone()
        if user:
            cursor.execute('UPDATE Usuario SET nome=%s, cpf=%s, senha=%s WHERE nome=%s', (novo_nome, novo_cpf, nova_senha, usuario))
            session['usuario'] = novo_nome  # Atualizar o nome do usuário na sessão
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Senha antiga incorreta'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao editar a conta: ' + str(e)})

# Rota para fazer logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Rota para gerenciar produtos
@app.route('/gerenciar')
def gerenciar():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    try:
        # Ajuste na consulta para trazer o nome do fornecedor associado a cada produto
        cursor.execute("""
            SELECT p.idProduto, p.nome, p.tamanho, p.cor, p.preco, p.quantidade, f.nome 
            FROM Produto p
            JOIN Fornecedor f ON p.idFornecedor = f.idFornecedor
        """)
        produtos = cursor.fetchall()

        cursor.execute("SELECT * FROM Produto WHERE quantidade < 24")
        produtos_baixo_estoque = cursor.fetchall()

        # Buscando os fornecedores no banco de dados
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return render_template('gerenciar.html', produtos=produtos, produtos_baixo_estoque=produtos_baixo_estoque, fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))



#ROTA PARA ADICIONAR PRODUTOS
@app.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'GET':
        # Buscando os fornecedores no banco de dados
        cursor.execute("SELECT idFornecedor, nome FROM Fornecedor")
        fornecedores = cursor.fetchall()

        # Debug: Verificar o conteúdo de fornecedores no console
        print(f"Fornecedores: {fornecedores}")

        # Renderizando o HTML com a lista de fornecedores
        return render_template('gerenciar.html', fornecedores=fornecedores)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute("""
                INSERT INTO Produto (nome, tamanho, cor, preco, quantidade, idFornecedor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor']))
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, message='Erro ao adicionar produto: ' + str(e))




@app.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    try:
        cursor.execute("SELECT * FROM Produto WHERE idProduto = %s", (id,))
        produto = cursor.fetchone()
        if produto:
            return jsonify(success=True, produto=dict(zip(['idProduto', 'nome', 'tamanho', 'cor', 'preco', 'quantidade', 'fornecedor'], produto)))
        else:
            return jsonify(success=False, message='Produto não encontrado')
    except Exception as e:
        return jsonify(success=False, message='Erro ao obter produto: ' + str(e))





@app.route('/produtos/editar/<int:id>', methods=['POST'])
def editar_produto(id):
    data = request.get_json()
    try:
        cursor.execute("""
            UPDATE Produto
            SET nome = %s, tamanho = %s, cor = %s, preco = %s, quantidade = %s, idFornecedor = %s
            WHERE idProduto = %s
        """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor'], id))
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message='Erro ao editar produto: ' + str(e))





@app.route('/produtos/deletar/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    try:
        cursor.execute("DELETE FROM Produto WHERE idProduto = %s", (id,))
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message='Erro ao deletar produto: ' + str(e))


@app.route('/produtos/pesquisar', methods=['GET'])
def pesquisar_produtos():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    nome_produto = request.args.get('nome', default='', type=str)
    print(f"Nome do produto pesquisado: {nome_produto}")  # Log para debug

    try:
        # Ajuste a consulta SQL para incluir o nome do fornecedor
        query = """
        SELECT p.idProduto, p.nome, p.tamanho, p.cor, p.preco, p.quantidade, f.nome AS fornecedor_nome
        FROM Produto p
        JOIN Fornecedor f ON p.idFornecedor = f.idFornecedor
        WHERE p.nome LIKE %s
        """
        cursor.execute(query, ('%' + nome_produto + '%',))
        produtos = cursor.fetchall()
        print(f"Produtos encontrados: {produtos}")  # Log para debug
        
        # Convertendo produtos para dicionário para retornar como JSON
        produtos_list = [
            {
                'id': produto[0],
                'nome': produto[1],
                'tamanho': produto[2],
                'cor': produto[3],
                'preco': produto[4],
                'quantidade': produto[5],
                'fornecedor_nome': produto[6]  # Nome do fornecedor
            }
            for produto in produtos
        ]
        
        return jsonify({'produtos': produtos_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    try:
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return render_template('fornecedores.html', fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

@app.route('/fornecedores', methods=['GET'])
def get_fornecedores():
    try:
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return jsonify(fornecedores)
    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/fornecedores/adicionar', methods=['POST'])
def adicionar_fornecedor():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        data = request.get_json()
        nome = data.get('nome')
        endereco = data.get('endereco')
        email = data.get('email')
        produtos = data.get('produtos')

        if None in [nome, endereco, email, produtos]:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'})

        cursor.execute("""
            INSERT INTO Fornecedor (nome, endereco, email, produtos)
            VALUES (%s, %s, %s, %s)
        """, (nome, endereco, email, produtos))
        return jsonify({'success': True, 'message': 'Fornecedor adicionado com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar fornecedor: {str(e)}'})

@app.route('/fornecedores/editar/<int:id>', methods=['POST'])
def editar_fornecedor(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    nome = data['nome']
    endereco = data['endereco']
    email = data['email']
    produtos = data['produtos']

    try:
        cursor.execute("UPDATE Fornecedor SET nome=%s, endereco=%s, email=%s, produtos=%s WHERE idFornecedor=%s", (nome, endereco, email, produtos, id))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao editar fornecedor: ' + str(e)})

@app.route('/fornecedores/deletar/<int:id>', methods=['POST'])
def deletar_fornecedor(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        cursor.execute("DELETE FROM Fornecedor WHERE idFornecedor=%s", (id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao deletar fornecedor: ' + str(e)})

@app.route('/fornecedores/pesquisar', methods=['GET'])
def pesquisar_fornecedor():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    nome_fornecedor = request.args.get('nome', default='', type=str)

    try:
        cursor.execute("SELECT * FROM Fornecedor WHERE nome LIKE %s", ('%' + nome_fornecedor + '%',))
        fornecedores = cursor.fetchall()
        return render_template('fornecedores.html', fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

@app.route('/extrato')
def extrato():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('extrato.html')


@app.route('/addvenda')
def add_venda():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('/addvenda.html')



# Função para conectar ao banco de dados
def conectar_db():
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='123456',
            database='testemonix78',
            autocommit=True
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql


app = Flask(__name__)
app.secret_key = 'sua_chave_secreta'  # Defina uma chave secreta para uso das sessões

# Configurações do banco de dados
db = pymysql.connect(host='localhost', user='root', password='123456', database='testemonix78', autocommit=True)
cursor = db.cursor()

# Função para verificar se o usuário está autenticado
def usuario_autenticado():
    return 'usuario' in session

# Rota para o login
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['senha']

        try:
            cursor.execute('SELECT * FROM Usuario WHERE nome=%s AND senha=%s', (username, password))
            user = cursor.fetchone()

            if user:
                session['usuario'] = username
                return jsonify({'success': True})  # Retorna um JSON indicando sucesso
            else:
                return jsonify({'success': False, 'message': 'Usuário ou senha incorretos'})
        except Exception as e:
            return jsonify({'success': False, 'message': 'Erro ao acessar o banco de dados: ' + str(e)})
    
    return render_template('login.html')

# Rota para o menu principal (requer autenticação)
@app.route('/')
def menu():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('menu.html')

# Rota para o registro de usuários
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        senha = request.form['senha']
        confirmar_senha = request.form['confirmar-senha']

        if senha == confirmar_senha:
            try:
                cursor.execute('INSERT INTO Usuario (cpf, senha, nome) VALUES (%s, %s, %s)', (cpf, senha, nome))
                return jsonify({'status': 'success'})  # Retorna um JSON indicando sucesso
            except Exception as e:
                return jsonify({'status': 'error', 'message': 'Erro ao acessar o banco de dados: ' + str(e)})
        else:
            return jsonify({'status': 'error', 'message': 'As senhas não coincidem'})  # Retorna um JSON indicando erro de senhas
    else:
        return render_template('registro.html')

# Rota para deletar conta
@app.route('/delete_account', methods=['POST'])
def delete_account():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    usuario = session['usuario']
    try:
        cursor.execute('DELETE FROM Usuario WHERE nome=%s', (usuario,))
        session.pop('usuario', None)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao deletar a conta: ' + str(e)})

# Rota para editar conta
@app.route('/edit_account', methods=['POST'])
def edit_account():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    usuario = session['usuario']
    senha_antiga = data['senha_antiga']
    nova_senha = data['nova_senha']
    novo_nome = data['novo_nome']
    novo_cpf = data['novo_cpf']

    try:
        cursor.execute('SELECT * FROM Usuario WHERE nome=%s AND senha=%s', (usuario, senha_antiga))
        user = cursor.fetchone()
        if user:
            cursor.execute('UPDATE Usuario SET nome=%s, cpf=%s, senha=%s WHERE nome=%s', (novo_nome, novo_cpf, nova_senha, usuario))
            session['usuario'] = novo_nome  # Atualizar o nome do usuário na sessão
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Senha antiga incorreta'})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao editar a conta: ' + str(e)})

# Rota para fazer logout
@app.route('/logout', methods=['GET'])
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

# Rota para gerenciar produtos
@app.route('/gerenciar')
def gerenciar():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    try:
        # Ajuste na consulta para trazer o nome do fornecedor associado a cada produto
        cursor.execute("""
            SELECT p.idProduto, p.nome, p.tamanho, p.cor, p.preco, p.quantidade, f.nome 
            FROM Produto p
            JOIN Fornecedor f ON p.idFornecedor = f.idFornecedor
        """)
        produtos = cursor.fetchall()

        cursor.execute("SELECT * FROM Produto WHERE quantidade < 24")
        produtos_baixo_estoque = cursor.fetchall()

        # Buscando os fornecedores no banco de dados
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return render_template('gerenciar.html', produtos=produtos, produtos_baixo_estoque=produtos_baixo_estoque, fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))



#ROTA PARA ADICIONAR PRODUTOS
@app.route('/produtos/adicionar', methods=['GET', 'POST'])
def adicionar_produto():
    if request.method == 'GET':
        # Buscando os fornecedores no banco de dados
        cursor.execute("SELECT idFornecedor, nome FROM Fornecedor")
        fornecedores = cursor.fetchall()

        # Debug: Verificar o conteúdo de fornecedores no console
        print(f"Fornecedores: {fornecedores}")

        # Renderizando o HTML com a lista de fornecedores
        return render_template('gerenciar.html', fornecedores=fornecedores)

    elif request.method == 'POST':
        data = request.get_json()
        try:
            cursor.execute("""
                INSERT INTO Produto (nome, tamanho, cor, preco, quantidade, idFornecedor)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor']))
            return jsonify(success=True)
        except Exception as e:
            return jsonify(success=False, message='Erro ao adicionar produto: ' + str(e))




@app.route('/produtos/<int:id>', methods=['GET'])
def obter_produto(id):
    try:
        cursor.execute("SELECT * FROM Produto WHERE idProduto = %s", (id,))
        produto = cursor.fetchone()
        if produto:
            return jsonify(success=True, produto=dict(zip(['idProduto', 'nome', 'tamanho', 'cor', 'preco', 'quantidade', 'fornecedor'], produto)))
        else:
            return jsonify(success=False, message='Produto não encontrado')
    except Exception as e:
        return jsonify(success=False, message='Erro ao obter produto: ' + str(e))





@app.route('/produtos/editar/<int:id>', methods=['POST'])
def editar_produto(id):
    data = request.get_json()
    try:
        cursor.execute("""
            UPDATE Produto
            SET nome = %s, tamanho = %s, cor = %s, preco = %s, quantidade = %s, idFornecedor = %s
            WHERE idProduto = %s
        """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor'], id))
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message='Erro ao editar produto: ' + str(e))





@app.route('/produtos/deletar/<int:id>', methods=['DELETE'])
def deletar_produto(id):
    try:
        cursor.execute("DELETE FROM Produto WHERE idProduto = %s", (id,))
        return jsonify(success=True)
    except Exception as e:
        return jsonify(success=False, message='Erro ao deletar produto: ' + str(e))


@app.route('/produtos/pesquisar', methods=['GET'])
def pesquisar_produtos():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    nome_produto = request.args.get('nome', default='', type=str)
    print(f"Nome do produto pesquisado: {nome_produto}")  # Log para debug

    try:
        # Ajuste a consulta SQL para incluir o nome do fornecedor
        query = """
        SELECT p.idProduto, p.nome, p.tamanho, p.cor, p.preco, p.quantidade, f.nome AS fornecedor_nome
        FROM Produto p
        JOIN Fornecedor f ON p.idFornecedor = f.idFornecedor
        WHERE p.nome LIKE %s
        """
        cursor.execute(query, ('%' + nome_produto + '%',))
        produtos = cursor.fetchall()
        print(f"Produtos encontrados: {produtos}")  # Log para debug
        
        # Convertendo produtos para dicionário para retornar como JSON
        produtos_list = [
            {
                'id': produto[0],
                'nome': produto[1],
                'tamanho': produto[2],
                'cor': produto[3],
                'preco': produto[4],
                'quantidade': produto[5],
                'fornecedor_nome': produto[6]  # Nome do fornecedor
            }
            for produto in produtos
        ]
        
        return jsonify({'produtos': produtos_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/fornecedores', methods=['GET'])
def listar_fornecedores():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    try:
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return render_template('fornecedores.html', fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

@app.route('/fornecedores', methods=['GET'])
def get_fornecedores():
    try:
        cursor.execute("SELECT * FROM Fornecedor")
        fornecedores = cursor.fetchall()
        return jsonify(fornecedores)
    except Exception as e:
        return jsonify({'error': str(e)})



@app.route('/fornecedores/adicionar', methods=['POST'])
def adicionar_fornecedor():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        data = request.get_json()
        nome = data.get('nome')
        endereco = data.get('endereco')
        email = data.get('email')
        produtos = data.get('produtos')

        if None in [nome, endereco, email, produtos]:
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'})

        cursor.execute("""
            INSERT INTO Fornecedor (nome, endereco, email, produtos)
            VALUES (%s, %s, %s, %s)
        """, (nome, endereco, email, produtos))
        return jsonify({'success': True, 'message': 'Fornecedor adicionado com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar fornecedor: {str(e)}'})

@app.route('/fornecedores/editar/<int:id>', methods=['POST'])
def editar_fornecedor(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    nome = data['nome']
    endereco = data['endereco']
    email = data['email']
    produtos = data['produtos']

    try:
        cursor.execute("UPDATE Fornecedor SET nome=%s, endereco=%s, email=%s, produtos=%s WHERE idFornecedor=%s", (nome, endereco, email, produtos, id))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao editar fornecedor: ' + str(e)})

@app.route('/fornecedores/deletar/<int:id>', methods=['POST'])
def deletar_fornecedor(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        cursor.execute("DELETE FROM Fornecedor WHERE idFornecedor=%s", (id,))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': 'Erro ao deletar fornecedor: ' + str(e)})

@app.route('/fornecedores/pesquisar', methods=['GET'])
def pesquisar_fornecedor():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    nome_fornecedor = request.args.get('nome', default='', type=str)

    try:
        cursor.execute("SELECT * FROM Fornecedor WHERE nome LIKE %s", ('%' + nome_fornecedor + '%',))
        fornecedores = cursor.fetchall()
        return render_template('fornecedores.html', fornecedores=fornecedores)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

@app.route('/extrato')
def extrato():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('extrato.html')


@app.route('/addvenda')
def add_venda():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    return render_template('/addvenda.html')

@app.route('/clientes')
def clientes():
    if not usuario_autenticado():
        return redirect(url_for('login'))

    try:
        cursor.execute("SELECT * FROM Cliente")
        clientes = cursor.fetchall()
        return render_template('clientes.html', clientes=clientes)
    except Exception as e:
        return render_template('erro.html', mensagem=str(e))

@app.route('/clientes/adicionar', methods=['POST'])
def adicionar_cliente():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    cidade = data.get('cidade')

    if None in [nome, cpf, cidade]:
        return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios.'})

    try:
        cursor.execute("""
            INSERT INTO Cliente (nome, cpf, cidade)
            VALUES (%s, %s, %s)
        """, (nome, cpf, cidade))
        return jsonify({'success': True, 'message': 'Cliente adicionado com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao adicionar cliente: {str(e)}'})

@app.route('/clientes/editar/<int:id>', methods=['POST'])
def editar_cliente(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    data = request.get_json()
    nome = data.get('nome')
    cpf = data.get('cpf')
    cidade = data.get('cidade')

    try:
        cursor.execute("""
            UPDATE Cliente
            SET nome = %s, cpf = %s, cidade = %s
            WHERE idCliente = %s
        """, (nome, cpf, cidade, id))
        return jsonify({'success': True, 'message': 'Cliente editado com sucesso.'})  # Corrigir chave 'message'
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao editar cliente: {str(e)}'})


@app.route('/clientes/deletar/<int:id>', methods=['DELETE'])
def deletar_cliente(id):
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    try:
        cursor.execute("DELETE FROM Cliente WHERE idCliente = %s", (id,))
        return jsonify({'success': True, 'message': 'Cliente deletado com sucesso.'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao deletar cliente: {str(e)}'})

@app.route('/clientes/pesquisar', methods=['GET'])
def pesquisar_clientes():
    if not usuario_autenticado():
        return jsonify({'success': False, 'message': 'Usuário não autenticado'})

    consulta = request.args.get('consulta')
    try:
        cursor.execute("SELECT * FROM Cliente WHERE nome LIKE %s", ('%' + consulta + '%',))
        clientes = cursor.fetchall()

        # Certifique-se de converter cada cliente em um dicionário
        lista_clientes = []
        for cliente in clientes:
            lista_clientes.append({
                'idCliente': cliente[0],
                'nome': cliente[1],
                'cpf': cliente[2],
                'cidade': cliente[3],
            })

        return jsonify({'success': True, 'clientes': lista_clientes})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao pesquisar clientes: {str(e)}'})


@app.route('/buscar_produto', methods=['GET'])
def buscar_produto():
    modelo = request.args.get('modelo')
    if modelo:
        try:
            cursor.execute("""
                SELECT idProduto, nome, tamanho, cor, preco, quantidade
                FROM Produto
                WHERE nome LIKE %s
            """, (f'%{modelo}%',))
            produtos = cursor.fetchall()
            if produtos:
                lista_produtos = []
                for produto in produtos:
                    idProduto, nome, tamanho, cor, preco, quantidade = produto
                    lista_produtos.append({
                        'idProduto': idProduto,
                        'nome': nome,
                        'tamanho': tamanho,
                        'cor': cor,
                        'preco': preco,
                        'quantidade': quantidade
                    })
                return jsonify({'success': True, 'produtos': lista_produtos})
            else:
                return jsonify({'success': False, 'message': 'Produto não encontrado'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao buscar produto: {str(e)}'})




@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    dados = request.get_json()
    itens = dados.get('itens', [])
    nome_cliente = dados.get('cliente')  # Captura o nome do cliente

    if not itens:
        return jsonify({'success': False, 'message': 'Carrinho vazio'})

    if not nome_cliente:
        return jsonify({'success': False, 'message': 'Por favor, insira o nome do cliente.'})

    try:
        cursor.execute("START TRANSACTION")

        for item in itens:
            idProduto = item['idProduto']
            quantidade_vendida = int(item['quantidade_vendida'])

            # Verificar estoque
            cursor.execute("SELECT quantidade FROM Produto WHERE idProduto = %s", (idProduto,))
            resultado = cursor.fetchone()
            if resultado:
                quantidade_atual = resultado[0]
            else:
                cursor.execute("ROLLBACK")
                return jsonify({'success': False, 'message': 'Produto não encontrado'})

            # Verifica se há estoque suficiente
            if quantidade_atual < quantidade_vendida:
                cursor.execute("ROLLBACK")
                return jsonify({'success': False, 'message': f'Estoque insuficiente para o produto ID {idProduto}'})

            nova_quantidade = quantidade_atual - quantidade_vendida
            cursor.execute("UPDATE Produto SET quantidade = %s WHERE idProduto = %s", (nova_quantidade, idProduto))

            valor_total = float(item['valor']) * quantidade_vendida

            # Inserir a compra com o nome do cliente
            cursor.execute("""
                INSERT INTO Compra (nomeCliente, idProduto, data, quantidade, valor)
                VALUES (%s, %s, CURDATE(), %s, %s)
            """, (nome_cliente, idProduto, quantidade_vendida, valor_total))

        cursor.execute("COMMIT")
        return jsonify({'success': True, 'message': 'Compra finalizada com sucesso'})
    except Exception as e:
        cursor.execute("ROLLBACK")
        return jsonify({'success': False, 'message': f'Erro ao finalizar compra: {str(e)}'})



@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    dados = request.get_json()
    itens = dados.get('itens', [])
    
    try:
        # Iniciar a transação
        cursor.execute("START TRANSACTION")
        
        # Atualizar a quantidade do produto no estoque
        for item in itens:
            idProduto = item['idProduto']
            quantidade_vendida = item['quantidade']
            
            # Buscar a quantidade atual do produto no estoque
            cursor.execute("SELECT quantidade FROM Produto WHERE idProduto = %s", (idProduto,))
            quantidade_atual = cursor.fetchone()[0]
            
            # Verificar se a quantidade do produto no estoque é suficiente
            if quantidade_atual < quantidade_vendida:
                cursor.execute("ROLLBACK")
                return jsonify({'success': False, 'message': 'Quantidade do produto no estoque é insuficiente'})
            
            # Atualizar a quantidade do produto no estoque
            nova_quantidade = quantidade_atual - quantidade_vendida
            cursor.execute("UPDATE Produto SET quantidade = %s WHERE idProduto = %s", (nova_quantidade, idProduto))
        
        # Adicionar o produto ao carrinho
        carrinho = session.get('carrinho', [])
        carrinho.append({
            'idProduto': idProduto,
            'quantidade': quantidade_vendida
        })
        session['carrinho'] = carrinho
        
        # Commitar a transação
        cursor.execute("COMMIT")
        
        return jsonify({'success': True, 'message': 'Produto adicionado ao carrinho com sucesso'})
    except Exception as e:
        # Rollback em caso de erro
        cursor.execute("ROLLBACK")
        return jsonify({'success': False, 'message': f'Erro ao adicionar produto ao carrinho: {str(e)}'})


@app.route('/remover_produto', methods=['POST'])
def remover_produto():
    dados = request.get_json()
    itens = dados.get('itens', [])
    
    try:
        # Iniciar a transação
        cursor.execute("START TRANSACTION")
        
        # Atualizar a quantidade do produto no estoque
        for item in itens:
            idProduto = item['idProduto']
            quantidade = item['quantidade']
            
            # Buscar a quantidade atual do produto no estoque
            cursor.execute("SELECT quantidade FROM Produto WHERE idProduto = %s", (idProduto,))
            quantidade_atual = cursor.fetchone()[0]
            
            # Atualizar a quantidade do produto no estoque
            nova_quantidade = quantidade_atual + quantidade
            cursor.execute("UPDATE Produto SET quantidade = %s WHERE idProduto = %s", (nova_quantidade, idProduto))
        
        # Remover o produto do carrinho
        carrinho = session.get('carrinho', [])
        carrinho.remove({
            'idProduto': idProduto,
            'quantidade': quantidade
        })
        session['carrinho'] = carrinho
        
        # Commitar a transação
        cursor.execute("COMMIT")
        
        return jsonify({'success': True, 'message': 'Produto removido do carrinho com sucesso'})
    except Exception as e:
        # Rollback em caso de erro
        cursor.execute("ROLLBACK")
        return jsonify({'success': False, 'message': f'Erro ao remover produto do carrinho: {str(e)}'})
    
    
if __name__ == '__main__':
    app.run(debug=True)