let carrinho = [];

// Função para buscar produtos
function buscarProduto() {
    const modelo = $('#modelo').val();
    if (modelo.length > 0) {
        $.ajax({
            url: '/buscar_produto',
            method: 'GET',
            data: { modelo: modelo },
            success: function(response) {
                $('#sugestoes').empty();
                if (response.success) {
                    response.produtos.forEach(produto => {
                        $('#sugestoes').append(`
                            <li class="list-group-item" onclick="selecionarProduto(${produto.idProduto}, '${produto.tamanho}', '${produto.cor}', ${produto.preco})">
                                ${produto.nome} - ${produto.tamanho} - ${produto.cor} - R$${produto.preco.toFixed(2)}
                            </li>
                        `);
                    });
                    $('#sugestoes').show();
                } else {
                    $('#sugestoes').hide();
                }
            },
            error: function() {
                alert('Erro ao buscar produto.');
            }
        });
    } else {
        $('#sugestoes').hide();
    }
}

// Função para selecionar um produto da lista
function selecionarProduto(idProduto, tamanho, cor, preco) {
    $('#modelo').val('');
    $('#tamanho').val(tamanho);
    $('#cor').val(cor);
    $('#valor').val(preco);
    $('#sugestoes').hide();
}

// Função para adicionar item ao carrinho
function adicionarItem() {
    const modelo = $('#modelo').val(); // Use o valor do modelo, ajuste conforme necessário
    const quantidade_vendida = $('#quantidade_vendida').val();
    const valor = $('#valor').val();
    const nome_cliente = $('#nome_cliente').val();

    if (!modelo || !quantidade_vendida || !nome_cliente) {
        alert('Preencha todos os campos antes de adicionar.');
        return;
    }

    carrinho.push({
        modelo: modelo, // Ajuste para o que você realmente quer adicionar
        quantidade_vendida: quantidade_vendida,
        valor: valor
    });

    // Atualizar a lista de itens no carrinho
    atualizarListaCarrinho();
}

// Função para atualizar a lista de itens no carrinho
function atualizarListaCarrinho() {
    const lista = $('#lista');
    lista.empty();
    carrinho.forEach(item => {
        lista.append(`<li class="list-group-item">${item.modelo} - Quantidade: ${item.quantidade_vendida}</li>`);
    });
}

// Função para finalizar a compra
function finalizarCompra() {
    const nome_cliente = $('#nome_cliente').val();

    if (carrinho.length === 0) {
        alert('Carrinho vazio!');
        return;
    }

    $.ajax({
        url: '/finalizar_compra',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ itens: carrinho, cliente: nome_cliente }),
        success: function(response) {
            if (response.success) {
                alert('Compra finalizada com sucesso!');
                // Limpar o carrinho e atualizar a UI
                carrinho = [];
                atualizarListaCarrinho();
                $('#nome_cliente').val('');
            } else {
                alert(response.message);
            }
        },
        error: function() {
            alert('Erro ao finalizar compra.');
        }
    });
}
