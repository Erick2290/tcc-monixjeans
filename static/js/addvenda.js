let carrinho = [];

// Função para desabilitar/abilitar campos
function toggleCamposProduto(habilitar) {
    $('#modelo').prop('disabled', !habilitar);
    $('#quantidade_vendida').prop('disabled', !habilitar);
    // Se tiver mais campos, adicione aqui
}

// Função para adicionar ao carrinho
function adicionarAoCarrinho() {
    const id = $('#produto_id').val();
    const modelo = $('#modelo').val();
    const quantidade = $('#quantidade_vendida').val();

    if (id && quantidade) {
        carrinho.push({ id: id, modelo: modelo, quantidade: quantidade });
        atualizarListaCarrinho();

        alert('Produto adicionado ao carrinho e campos de produto serão limpos.');

        $('#modelo').val(''); 
        $('#quantidade_vendida').val('');
        $('#produto_id').val('');
        $('#tamanho').val('');
        $('#cor').val('');
        $('#valor').val('');
        $('#quantidade_disponivel').val('');
    } else {
        alert('Por favor, preencha todos os campos do produto.');
    }
}

// Função para atualizar a lista do carrinho
function atualizarListaCarrinho() {
    $('#lista').empty();
    carrinho.forEach(function(item) {
        $('#lista').append('<li class="list-group-item">' + item.modelo + ' - Quantidade: ' + item.quantidade + '</li>');
    });
}

// Função para buscar produtos
function buscarProduto() {
    const modelo = $('#modelo').val();
    if (modelo.length > 0) {
        $.ajax({
            url: '/buscar_produto',
            method: 'GET',
            data: { modelo: modelo },
            success: function(data) {
                $('#sugestoes').empty().show();
                data.forEach(function(produto) {
                    $('#sugestoes').append(
                        '<li class="list-group-item" onclick="selecionarProduto(\'' + produto.nome + '\', \'' + produto.tamanho + '\', \'' + produto.cor + '\', ' + produto.preco + ', ' + produto.idProduto + ', ' + produto.quantidade + ')">' + 
                        produto.nome + 
                        ' (Qt=' + produto.quantidade + ', $=' + produto.preco + ', Tm=' + produto.tamanho + ', Cor=' + produto.cor + ')</li>'
                    );
                });
            }
        });
    } else {
        $('#sugestoes').hide();
    }
}

// Função para buscar produtos no modal de edição
function buscarProdutoModal() {
    const modelo = $('#produto').val();
    if (modelo.length > 0) {
        $.ajax({
            url: '/buscar_produto',
            method: 'GET',
            data: { modelo: modelo },
            success: function(data) {
                $('#sugestoes_produtos_modal').empty().show();
                data.forEach(function(produto) {
                    $('#sugestoes_produtos_modal').append(
                        '<li class="list-group-item" onclick="selecionarProdutoModal(\'' + produto.nome + '\', \'' + produto.tamanho + '\', \'' + produto.cor + '\', ' + produto.preco + ', ' + produto.idProduto + ', ' + produto.quantidade + ')">' + 
                        produto.nome + 
                        ' (Qt=' + produto.quantidade + ', $=' + produto.preco + ', Tm=' + produto.tamanho + ', Cor=' + produto.cor + ')</li>'
                    );
                });
            }
        });
    } else {
        $('#sugestoes_produtos_modal').hide();
    }
}

// Função para selecionar produto no modal de edição
function selecionarProdutoModal(nome, tamanho, cor, preco, id, quantidade) {
    $('#produto').val(nome);
    $('#tamanho_modal').val(tamanho);
    $('#cor_modal').val(cor);
    $('#valor_modal').val(preco);
    $('#produto_id_modal').val(id);
    $('#quantidade_disponivel_modal').val(quantidade);
    $('#sugestoes_produtos_modal').hide();
}

// Função para selecionar produto
function selecionarProduto(nome, tamanho, cor, preco, id, quantidade) {
    $('#modelo').val(nome);
    $('#tamanho').val(tamanho);
    $('#cor').val(cor);
    $('#valor').val(preco);
    $('#produto_id').val(id);
    $('#quantidade_disponivel').val(quantidade); // Atualiza a quantidade disponível
    $('#sugestoes').hide();
}

// Função para buscar cliente
function buscarCliente() {
    const nome = $('#nome_cliente').val();
    if (nome.length > 0) {
        $.ajax({
            url: '/buscar_cliente',
            method: 'GET',
            data: { nome: nome },
            success: function(data) {
                $('#sugestoes_clientes').empty().show();
                data.forEach(function(cliente) {
                    $('#sugestoes_clientes').append('<li class="list-group-item" onclick="selecionarCliente(\'' + cliente.nome + '\', \'' + cliente.cpf + '\')">' + cliente.nome + '</li>');
                });
            }
        });
    } else {
        $('#sugestoes_clientes').hide();
    }
}

// Função para buscar clientes no modal de edição
function buscarClienteModal() {
    const nome = $('#cliente').val();
    if (nome.length > 0) {
        $.ajax({
            url: '/buscar_cliente',
            method: 'GET',
            data: { nome: nome },
            success: function(data) {
                $('#sugestoes_clientes_modal').empty().show();
                data.forEach(function(cliente) {
                    $('#sugestoes_clientes_modal').append('<li class="list-group-item" onclick="selecionarClienteModal(\'' + cliente.nome + '\')">' + cliente.nome + '</li>');
                });
            }
        });
    } else {
        $('#sugestoes_clientes_modal').hide();
    }
}

// Função para selecionar cliente no modal de edição
function selecionarClienteModal(nome) {
    $('#cliente').val(nome);
    $('#sugestoes_clientes_modal').hide();
}

// Função para selecionar cliente
function selecionarCliente(nome, cpf) {
    $('#nome_cliente').val(nome);
    $('#cpf_cliente').val(cpf); // Campo oculto para armazenar CPF
    $('#sugestoes_clientes').hide();
    toggleCamposProduto(true);
}

// Função para finalizar compra
function finalizarCompra() {
    const cpf_cliente = $('#cpf_cliente').val();
    const data_venda = $('#data_venda').val();
    const carrinhoData = carrinho.map(item => `${item.id},${item.quantidade}`);

    $.ajax({
        url: '/finalizar_compra',
        method: 'POST',
        data: {
            cpf_cliente: cpf_cliente,
            data_venda: data_venda,
            'carrinho[]': carrinhoData
        },
        success: function(response) {
            if (response.success) {
                alert('Compra finalizada com sucesso!');
                carrinho = [];
                atualizarListaCarrinho();
                listarVendas();

                $('#nome_cliente').val('');
                $('#cpf_cliente').val('');
                $('#modelo').val(''); 
                $('#quantidade_vendida').val('');
                $('#produto_id').val('');
                $('#tamanho').val('');
                $('#cor').val('');
                $('#valor').val('');
                $('#quantidade_disponivel').val('');

                toggleCamposProduto(false);
            }
        },
        error: function() {
            alert('Erro ao finalizar a compra.');
        }
    });
}


document.querySelector('form[action="/pesquisar_vendas"]').addEventListener('submit', function(e) {
    e.preventDefault(); // Impede o envio padrão do formulário
    const nome = this.querySelector('input[name="nome"]').value;

    if (nome.trim() === '') {
        listarVendas(true); // Chama listarVendas com uma flag para buscar a lista original
    } else {
        // Se não estiver vazio, faz a busca
        fetch(`/pesquisar_vendas?nome=${encodeURIComponent(nome)}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            if (data.vendas && data.vendas.length > 0) {
                const listaVendas = document.getElementById('lista-vendas');
                listaVendas.innerHTML = '';
                data.vendas.forEach(venda => {
                    listaVendas.innerHTML += `
                        <li data-id="${venda.idCompra}">
                            <h3>${venda.produto}</h3>
                            <p><strong>Cliente:</strong> ${venda.cliente}</p>
                            <p><strong>Data:</strong> ${venda.data}</p>
                            <p><strong>Quantidade:</strong> ${venda.quantidade}</p>
                            <p><strong>Valor:</strong> ${venda.valor}R$</p>
                            <div class="button-group">
                                <button class="btn btn-warning btn-sm" onclick="abrirModalEditarVenda(${venda.idCompra})">Editar</button>
                                <button class="btn btn-warning btn-sm" onclick="deletarVenda(${venda.idCompra})">Excluir</button>
                            </div>
                        </li>
                    `;
                });
            } else {
                alert('Nenhuma venda encontrada.');
            }
        })
        .catch(error => {
            alert('Ocorreu um erro ao pesquisar vendas: ' + error.message);
        });
    }
});


function listarVendas(buscarListaOriginal = false) {
    if (buscarListaOriginal) {
        $.ajax({
            url: '/vendas',
            method: 'GET',
            success: function(data) {
                const listaVendas = document.getElementById('lista-vendas');
                listaVendas.innerHTML = '';
                data.forEach(function(venda) {
                    listaVendas.innerHTML += `
                        <li data-id="${venda.idCompra}">
                            <h3>${venda.produto}</h3>
                            <p><strong>Cliente:</strong> ${venda.cliente}</p>
                            <p><strong>Data:</strong> ${venda.data}</p>
                            <p><strong>Quantidade:</strong> ${venda.quantidade}</p>
                            <p><strong>Valor:</strong> ${venda.valor}R$</p>
                            <div class="button-group">
                                <button class="btn btn-warning btn-sm" onclick="abrirModalEditarVenda(${venda.idCompra})">Editar</button>
                                <button class="btn btn-warning btn-sm" onclick="deletarVenda(${venda.idCompra})">Excluir</button>
                            </div>
                        </li>
                    `;
                });
            }
        });
    } else {
        $.ajax({
            url: '/vendas',
            method: 'GET',
            success: function(data) {
                const listaVendas = document.getElementById('lista-vendas');
                listaVendas.innerHTML = '';
                data.forEach(function(venda) {
                    listaVendas.innerHTML += `
                        <li data-id="${venda.idCompra}">
                            <h3>${venda.produto}</h3>
                            <p><strong>Cliente:</strong> ${venda.cliente}</p>
                            <p><strong>Data:</strong> ${venda.data}</p>
                            <p><strong>Quantidade:</strong> ${venda.quantidade}</p>
                            <p><strong>Valor:</strong> ${venda.valor}R$</p>
                            <div class="button-group">
                                <button class="btn btn-warning btn-sm" onclick="abrirModalEditarVenda(${venda.idCompra})">Editar</button>
                                <button class="btn btn-warning btn-sm" onclick="deletarVenda(${venda.idCompra})">Excluir</button>
                            </div>
                        </li>
                    `;
                });
            }
        });
    }
}

// Chamar listarVendas na inicialização da página
$(document).ready(function() {
    listarVendas();
    toggleCamposProduto(false);

    const dataAtual = new Date();
    const dia = String(dataAtual.getDate()).padStart(2, '0');
    const mes = String(dataAtual.getMonth() + 1).padStart(2, '0');
    const ano = dataAtual.getFullYear();
    const dataFormatadaParaInput = `${ano}-${mes}-${dia}`;
    $('#data_venda').val(dataFormatadaParaInput);
});

// Função para abrir modal de edição
function abrirModalEditarVenda(id) {
    $.ajax({
        url: '/vendas/' + id,
        method: 'GET',
        success: function(data) {
            $('#modalEditarVenda').modal('show');
            $('#idCompra').val(data.idCompra);
            $('#cliente').val(data.cliente);
            $('#produto').val(data.produto);
            const [ano, mes, dia] = data.data.split('-');
            $('#data_venda_modal').val(`${dia}-${mes}-${ano}`);                      
            $('#quantidade').val(data.quantidade);
            $('#valor_modal').val(data.valor);
            
            // Preenchendo os campos adicionais
            if (data.tamanho) {
                $('#tamanho_modal').val(data.tamanho);
            }
            if (data.cor) {
                $('#cor_modal').val(data.cor);
            }1

            // Buscar a quantidade disponível do produto
            $.ajax({
                url: '/buscar_produto',
                method: 'GET',
                data: { modelo: data.produto },
                success: function(produtos) {
                    produtos.forEach(function(produto) {
                        if (produto.nome === data.produto) {
                            $('#quantidade_disponivel_modal').val(produto.quantidade);
                        }
                    });
                }
            });
        },
        error: function() {
            alert('Erro ao carregar os dados da venda.');
        }
    });
}

// Função para atualizar a venda
// Função para atualizar a venda
function atualizarVenda(id) {
    const quantidade = $('#quantidade').val();

    if (isNaN(quantidade) || quantidade <= 0) {
        alert('Por favor, insira uma quantidade válida.');
        return;
    }

    $.ajax({
        url: '/atualizar_venda/' + id,
        method: 'PUT',
        contentType: 'application/json',
        data: JSON.stringify({ quantidade: quantidade }),
        success: function(response) {
            if (response.success) {
                alert('Venda atualizada com sucesso!');
                listarVendas();  // Atualiza a lista de vendas
                $('#modalEditarVenda').modal('hide');  // Fecha o modal

                // Atualizar a quantidade disponível do produto
                $.ajax({
                    url: '/buscar_produto',
                    method: 'GET',
                    data: { modelo: $('#produto').val() },
                    success: function(produtos) {
                        produtos.forEach(function(produto) {
                            if (produto.nome === $('#produto').val()) {
                                $('#quantidade_disponivel_modal').val(produto.quantidade);
                            }
                        });
                    }
                });
            }
        },
        error: function() {
            alert('Erro ao atualizar a venda.');
        }
    });
}
// Função para deletar venda
function deletarVenda(id) {
    if (confirm('Tem certeza que deseja deletar esta venda?')) {
        $.ajax({
            url: '/deletar_venda/' + id,
            method: 'DELETE',
            success: function(response) {
                if (response.success) {
                    alert('Venda deletada com sucesso!');
                    listarVendas(); 
                } else {
                    alert(response.message);
                }
            },
            error: function() {
                alert('Erro ao deletar a venda.');
            }
        });
    }
}

// Função para cancelar o carrinho
function cancelarCarrinho() {
    carrinho = [];
    atualizarListaCarrinho(); 
    
    $('#modelo').val(''); 
    $('#quantidade_vendida').val(''); 
    $('#produto_id').val('');
    $('#tamanho').val('');
    $('#cor').val('');
    $('#valor').val('');
    $('#quantidade_disponivel').val('');
    
    $('#nome_cliente').val('');
    $('#cpf_cliente').val('');

    toggleCamposProduto(false);

    alert('Carrinho cancelado.');
}
