from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql
from datetime import date, datetime

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


@app.route('/gerenciar/fornecedores/pesquisar', methods=['GET'])
def pesquisar_fornecedores():
    nome_fornecedor = request.args.get('nome', default='', type=str)
    
    try:
        cursor.execute("SELECT idFornecedor, nome FROM Fornecedor WHERE nome LIKE %s", ('%' + nome_fornecedor + '%',))
        fornecedores = cursor.fetchall()

        # Convertendo fornecedores para dicionário para retornar como JSON
        fornecedores_list = [{'id': fornecedor[0], 'nome': fornecedor[1]} for fornecedor in fornecedores]
        
        return jsonify({'fornecedores': fornecedores_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



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
            """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor_id']))
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
        """, (data['nome'], data['tamanho'], data['cor'], data['preco'], data['quantidade'], data['fornecedor_id'], id))
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




#ROTAS DE ADDVENDA


@app.route('/addvenda')
def add_venda():
    if not usuario_autenticado():
        return redirect(url_for('login'))
    
    # Busca as vendas
    cursor.execute("""
        SELECT c.idCompra, cl.nome, p.nome, c.data, c.quantidade, (c.quantidade * p.preco) AS valor
        FROM Compra c
        JOIN Cliente cl ON c.idCliente = cl.idCliente
        JOIN Produto p ON c.idProduto = p.idProduto
    """)
    vendas = cursor.fetchall()
    
    # Formatar os dados das vendas para retornar como JSON
    vendas_dict = [
        {
            'idCompra': v[0],
            'cliente': v[1],
            'produto': v[2],
            'data': v[3].strftime('%d-%m-%Y'),  # Formata a data para 'YYYY-MM-DD'
            'quantidade': v[4],
            'valor': v[5]
        } for v in vendas
    ]
    
    return render_template('addvenda.html', vendas=vendas_dict)
@app.route('/buscar_produto')
def buscar_produto():
    modelo = request.args.get('modelo')
    cursor.execute("SELECT idProduto, nome, tamanho, cor, preco, quantidade FROM Produto WHERE nome LIKE %s", ('%' + modelo + '%',))
    produtos = cursor.fetchall()
    produtos_dict = [{'idProduto': p[0], 'nome': p[1], 'tamanho': p[2], 'cor': p[3], 'preco': p[4], 'quantidade': p[5]} for p in produtos]
    return jsonify(produtos_dict)

@app.route('/buscar_cliente')
def buscar_cliente():
    nome = request.args.get('nome')
    cursor.execute("SELECT idCliente, nome, cpf FROM Cliente WHERE nome LIKE %s", ('%' + nome + '%',))
    clientes = cursor.fetchall()
    clientes_dict = [{'idCliente': c[0], 'nome': c[1], 'cpf': c[2]} for c in clientes]
    return jsonify(clientes_dict)

@app.route('/finalizar_compra', methods=['POST'])
def finalizar_compra():
    cliente_cpf = request.form.get('cpf_cliente')
    data_venda = request.form.get('data_venda')  # Obtendo a data da venda
    carrinho = request.form.getlist('carrinho[]')
    data_venda_formatada = datetime.strptime(data_venda, '%Y-%m-%d').date()  # Convertendo para o formato adequado

    try:
        for item in carrinho:
            produto_id, quantidade = item.split(',')
            quantidade = int(quantidade)

            # Verifica a quantidade disponível do produto
            cursor.execute("SELECT quantidade FROM Produto WHERE idProduto = %s", (produto_id,))
            quantidade_estoque = cursor.fetchone()

            if quantidade_estoque and quantidade_estoque[0] >= quantidade:
                # Busca o preço do produto
                cursor.execute("SELECT preco FROM Produto WHERE idProduto = %s", (produto_id,))
                preco = cursor.fetchone()

                if preco:
                    preco = preco[0]
                    valor_total = preco * quantidade

                    # Insere a venda na tabela Compra
                    cursor.execute(
                        "INSERT INTO Compra (idCliente, idProduto, data, quantidade, valor) VALUES ((SELECT idCliente FROM Cliente WHERE cpf = %s), %s, %s, %s, %s)",
                        (cliente_cpf, produto_id, data_venda_formatada, quantidade, valor_total)
                    )

                    # Atualiza o estoque do produto
                    cursor.execute(
                        "UPDATE Produto SET quantidade = quantidade - %s WHERE idProduto = %s",
                        (quantidade, produto_id)
                    )

                else:
                    return jsonify({'success': False, 'message': 'Produto não encontrado'})

            else:
                return jsonify({'success': False, 'message': 'Quantidade insuficiente em estoque'})

        # Faz o commit da transação
        db.commit()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erro ao finalizar a compra: {str(e)}")
        db.rollback()
        return jsonify({'success': False, 'message': 'Erro ao finalizar a compra', 'error': str(e)}), 500
    
    except Exception as e:
        # Log de erro detalhado
        print(f"Erro ao finalizar a compra: {str(e)}")
        db.rollback()  # Desfaz as alterações se ocorrer um erro
        return jsonify({'success': False, 'message': 'Erro ao finalizar a compra', 'error': str(e)}), 500




# Read venda específica pelo ID
@app.route('/vendas/<int:id>', methods=['GET'])
def buscar_venda(id):
    cursor.execute("""
        SELECT c.idCompra, cl.nome, p.nome, p.tamanho, p.cor, p.preco, c.data, c.quantidade, (c.quantidade * p.preco) AS valor
        FROM Compra c
        JOIN Cliente cl ON c.idCliente = cl.idCliente
        JOIN Produto p ON c.idProduto = p.idProduto
        WHERE c.idCompra = %s
    """, (id,))
    venda = cursor.fetchone()

    if venda:
        venda_dict = {
            'idCompra': venda[0],
            'cliente': venda[1],
            'produto': venda[2],
            'tamanho': venda[3],
            'cor': venda[4],
            'preco': venda[5],
            'data': venda[6].strftime('%d-%m-%Y'),  # Formata a data para 'DD-MM-YYYY'
            'quantidade': venda[7],
            'valor': venda[8]
        }
        return jsonify(venda_dict)
    else:
        return jsonify({'success': False, 'message': 'Venda não encontrada'}), 404



# Read vendas
@app.route('/vendas', methods=['GET'])
def listar_vendas():
    cursor.execute("""
        SELECT c.idCompra, cl.nome, p.nome, c.data, c.quantidade, (c.quantidade * p.preco) AS valor
        FROM Compra c
        JOIN Cliente cl ON c.idCliente = cl.idCliente
        JOIN Produto p ON c.idProduto = p.idProduto
        WHERE c.idCompra = %s
    """, (id,))
    venda = cursor.fetchone()
    
    if not venda:
        return jsonify({'success': False, 'message': 'Venda não encontrada'}), 404
    
    venda_dict = {
        'idCompra': venda[0],
        'cliente': venda[1],
        'produto': venda[2],
        'data': venda[3].strftime('%Y-%m-%d'),  # Ajuste o formato de data, se necessário
        'quantidade': venda[4],
        'valor': venda[5]
    }
    
    return jsonify(venda_dict)


# Update venda
@app.route('/atualizar_venda/<int:id>', methods=['PUT'])
def atualizar_venda(id):
    dados = request.get_json()
    nova_quantidade = int(dados.get('quantidade'))  # Converta para inteiro

    # Primeiro, obtenha a quantidade atual da venda
    cursor.execute("SELECT quantidade, idProduto FROM Compra WHERE idCompra = %s", (id,))
    venda = cursor.fetchone()

    if not venda:
        return jsonify({'success': False, 'message': 'Venda não encontrada'}), 404

    quantidade_atual = venda[0]
    produto_id = venda[1]

    try:
        if nova_quantidade > quantidade_atual:
            # Retira a diferença da tabela Produto
            diferenca = nova_quantidade - quantidade_atual
            cursor.execute("UPDATE Produto SET quantidade = quantidade - %s WHERE idProduto = %s", (diferenca, produto_id))
        elif nova_quantidade < quantidade_atual:
            # Adiciona a diferença de volta à tabela Produto
            diferenca = quantidade_atual - nova_quantidade
            cursor.execute("UPDATE Produto SET quantidade = quantidade + %s WHERE idProduto = %s", (diferenca, produto_id))

        # Atualiza a quantidade e o valor na tabela Compra
        cursor.execute("SELECT preco FROM Produto WHERE idProduto = %s", (produto_id,))
        preco_unitario = cursor.fetchone()

        if not preco_unitario:
            return jsonify({'success': False, 'message': 'Produto não encontrado'}), 404

        preco_unitario = preco_unitario[0]
        cursor.execute("UPDATE Compra SET quantidade = %s, valor = %s WHERE idCompra = %s",
                       (nova_quantidade, nova_quantidade * preco_unitario, id))

        return jsonify({'success': True})
    except Exception as e:
        # Log detalhado do erro
        print(f"Erro ao atualizar venda: {str(e)}")  # Log do erro no console
        return jsonify({'success': False, 'message': 'Erro ao atualizar a venda', 'error': str(e)}), 500

# Delete venda
@app.route('/deletar_venda/<int:id>', methods=['DELETE'])
def deletar_venda(id):
    try:
        # Primeiro, recupera a venda que será deletada
        cursor.execute("SELECT quantidade, idProduto FROM Compra WHERE idCompra = %s", (id,))
        venda = cursor.fetchone()

        if not venda:
            return jsonify({'success': False, 'message': 'Venda não encontrada'}), 404

        quantidade_vendida = venda[0]
        produto_id = venda[1]

        # Adiciona a quantidade de volta ao estoque
        cursor.execute("UPDATE Produto SET quantidade = quantidade + %s WHERE idProduto = %s", (quantidade_vendida, produto_id))

        # Agora, deleta a venda da tabela Compra
        cursor.execute("DELETE FROM Compra WHERE idCompra = %s", (id,))

        # Faz o commit da transação
        db.commit()

        return jsonify({'success': True})

    except Exception as e:
        # Log de erro detalhado
        print(f"Erro ao deletar venda: {str(e)}")
        db.rollback()  # Desfaz as alterações se ocorrer um erro
        return jsonify({'success': False, 'message': 'Erro ao deletar a venda', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)