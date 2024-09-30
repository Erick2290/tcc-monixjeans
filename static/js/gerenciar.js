document.addEventListener('DOMContentLoaded', function () {
    const adicionarProdutoForm = document.getElementById('adicionarProdutoForm');
    const editarProdutoForm = document.getElementById('editarProdutoForm');

    function toggleLoadingState(isLoading, form) {
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = isLoading;
        submitButton.textContent = isLoading ? 'Aguarde...' : 'Enviar';
    }

    adicionarProdutoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        toggleLoadingState(true, adicionarProdutoForm);
    
        const formData = new FormData(adicionarProdutoForm);
        const data = Object.fromEntries(formData.entries());
    
        // Log do ID do fornecedor para depuração
        console.log('ID do fornecedor:', data.fornecedor_id); // Verifique se o ID do fornecedor está correto

        fetch('/produtos/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            toggleLoadingState(false, adicionarProdutoForm);
            if (data.success) {
                window.location.reload();
            } else {
                alert('Erro ao adicionar produto: ' + data.message);
            }
        })
        .catch(error => {
            toggleLoadingState(false, adicionarProdutoForm);
            alert('Ocorreu um erro: ' + error.message);
        });
    });

    window.abrirModalEditar = function (id) {
        fetch(`/produtos/${id}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            if (data.produto) {
                const produto = data.produto;
                document.getElementById('produtoId').value = produto.idProduto;
                document.getElementById('editNome').value = produto.nome;
                document.getElementById('editTamanho').value = produto.tamanho;
                document.getElementById('editCor').value = produto.cor;
                document.getElementById('editPreco').value = produto.preco;
                document.getElementById('editQuantidade').value = produto.quantidade;
                document.getElementById('fornecedor_id_edit').value = produto.fornecedor; // Corrigir para usar 'fornecedor'
                const editarProdutoModal = new bootstrap.Modal(document.getElementById('editarProdutoModal'));
                editarProdutoModal.show();
            } else {
                alert('Erro ao carregar produto: ' + data.message);
            }
        })
        .catch(error => {
            alert('Ocorreu um erro ao carregar o produto: ' + error.message);
        });
    };

    editarProdutoForm.addEventListener('submit', function (e) {
        e.preventDefault();
        toggleLoadingState(true, editarProdutoForm);

        const id = document.getElementById('produtoId').value;
        const formData = new FormData(editarProdutoForm);
        const data = Object.fromEntries(formData.entries());

        fetch(`/produtos/editar/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(data => {
            toggleLoadingState(false, editarProdutoForm);
            if (data.success) {
                window.location.reload();
            } else {
                alert('Erro ao editar produto: ' + data.message);
            }
        })
        .catch(error => {
            toggleLoadingState(false, editarProdutoForm);
            alert('Ocorreu um erro ao editar o produto: ' + error.message);
        });
    });

    window.deletarProduto = function (id) {
        if (confirm('Tem certeza que deseja excluir este produto?')) {
            fetch(`/produtos/deletar/${id}`, {
                method: 'DELETE',
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } else {
                    alert('Erro ao deletar produto: ' + data.message);
                }
            })
            .catch(error => {
                alert('Ocorreu um erro ao deletar o produto: ' + error.message);
            });
        }
    };

    document.querySelector('form[action="/produtos/pesquisar"]').addEventListener('submit', function(e) {
        e.preventDefault();
        const nome = this.querySelector('input[name="nome"]').value;
    
        fetch(`/produtos/pesquisar?nome=${encodeURIComponent(nome)}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            if (data.produtos && data.produtos.length > 0) {
                const listaProdutos = document.getElementById('lista-produtos');
                listaProdutos.innerHTML = '';
                data.produtos.forEach(produto => {
                    listaProdutos.innerHTML += `
                        <li data-id="${produto.id}">
                            <h3>${produto.nome}</h3>
                            <p><strong>Tamanho:</strong> ${produto.tamanho}</p>
                            <p><strong>Cor:</strong> ${produto.cor}</p>
                            <p><strong>Preço:</strong> ${produto.preco}</p>
                            <p><strong>Quantidade:</strong> ${produto.quantidade}</p>
                            <p><strong>Fornecedor:</strong> ${produto.fornecedor_nome}</p>
                            <button onclick="abrirModalEditar(${produto.id})">Editar</button>
                            <button onclick="deletarProduto(${produto.id})">Excluir</button>
                        </li>
                    `;
                });
            } else {
                alert('Nenhum produto encontrado.');
            }
        })
        .catch(error => {
            alert('Ocorreu um erro ao pesquisar produtos: ' + error.message);
        });
    });
    
    // Função para pesquisar fornecedores
    document.getElementById('fornecedorPesquisa').addEventListener('input', function() {
        pesquisarFornecedores(); // Chame a função aqui
    });

    function pesquisarFornecedores() {
        const nome = document.getElementById('fornecedorPesquisa').value || document.getElementById('fornecedorPesquisaEdit').value;
        
        $.ajax({
            url: `/gerenciar/fornecedores/pesquisar`,
            method: 'GET',
            data: { nome: nome },
            success: function(data) {
                const fornecedorSelect = document.getElementById('fornecedor_id');
                fornecedorSelect.innerHTML = '<option value="">Selecione um fornecedor</option>'; // Resetar opções
                
                const listaFornecedores = document.getElementById('listaFornecedores');
                listaFornecedores.innerHTML = ''; // Limpar a lista existente
                listaFornecedores.style.display = 'none'; // Ocultar a lista por padrão
    
                if (data.fornecedores && data.fornecedores.length > 0) {
                    data.fornecedores.forEach(fornecedor => {
                        fornecedorSelect.innerHTML += `
                            <option value="${fornecedor.id}">${fornecedor.nome}</option>
                        `;
    
                        // Adicionar opções à lista de fornecedores
                        const listItem = document.createElement('li');
                        listItem.className = 'list-group-item';
                        listItem.textContent = fornecedor.nome;
                        listItem.onclick = function() {
                            // Ao clicar, definir o fornecedor na entrada
                            document.getElementById('fornecedorPesquisa').value = fornecedor.nome;
                            fornecedorSelect.value = fornecedor.id; // Selecionar o fornecedor no select
                            document.getElementById('fornecedor_id').value = fornecedor.id; // Atribuir o ID do fornecedor ao campo oculto
                            listaFornecedores.style.display = 'none'; // Ocultar a lista
                        };
                        listaFornecedores.appendChild(listItem);
                    });
                    listaFornecedores.style.display = 'block'; // Exibir a lista
                } else {
                    fornecedorSelect.innerHTML += '<option value="">Nenhum fornecedor encontrado</option>';
                }
            },
            error: function(xhr, status, error) {
                console.error('Erro ao pesquisar fornecedores:', error);
            }
        });
    }
    
});


$(document).ready(function() {
    // Pesquisa de fornecedores no modal de edição
    $('#fornecedorPesquisaEdit').on('input', function() {
        let nomeFornecedor = $(this).val();
        if (nomeFornecedor.length > 0) {
            $.ajax({
                url: '/gerenciar/fornecedores/pesquisar',
                method: 'GET',
                data: { nome: nomeFornecedor },
                success: function(response) {
                    let fornecedores = response.fornecedores;
                    let lista = $('#listaFornecedoresEdit');
                    lista.empty(); // Limpa a lista existente
                    if (fornecedores.length > 0) {
                        fornecedores.forEach(function(fornecedor) {
                            lista.append(`<li class="list-group-item" data-id="${fornecedor.id}">${fornecedor.nome}</li>`);
                        });
                        lista.show(); // Mostra a lista
                    } else {
                        lista.hide(); // Esconde a lista se não houver fornecedores
                    }
                },
                error: function() {
                    alert('Erro ao buscar fornecedores.');
                }
            });
        } else {
            $('#listaFornecedoresEdit').hide(); // Esconde a lista se o campo estiver vazio
        }
    });

    // Selecionar fornecedor da lista
    $(document).on('click', '#listaFornecedoresEdit .list-group-item', function() {
        let idFornecedor = $(this).data('id');
        let nomeFornecedor = $(this).text();
        $('#fornecedorPesquisaEdit').val(nomeFornecedor); // Define o nome no campo de pesquisa
        $('#fornecedor_id_edit').val(idFornecedor); // Define o ID do fornecedor oculto
        $('#listaFornecedoresEdit').hide(); // Esconde a lista
    });
});

$(document).ready(function() {
    // Pesquisa de fornecedores no modal de edição
    $('#fornecedorPesquisaEdit').on('input', function() {
        let nomeFornecedor = $(this).val();
        if (nomeFornecedor.length > 0) {
            $.ajax({
                url: '/gerenciar/fornecedores/pesquisar',
                method: 'GET',
                data: { nome: nomeFornecedor },
                success: function(response) {
                    let fornecedores = response.fornecedores;
                    let lista = $('#listaFornecedoresEdit');
                    lista.empty(); // Limpa a lista existente
                    if (fornecedores.length > 0) {
                        fornecedores.forEach(function(fornecedor) {
                            lista.append(`<li class="list-group-item" data-id="${fornecedor.id}">${fornecedor.nome}</li>`);
                        });
                        lista.show(); // Mostra a lista
                    } else {
                        lista.hide(); // Esconde a lista se não houver fornecedores
                    }
                },
                error: function() {
                    alert('Erro ao buscar fornecedores.');
                }
            });
        } else {
            $('#listaFornecedoresEdit').hide(); // Esconde a lista se o campo estiver vazio
        }
    });

    // Selecionar fornecedor da lista
    $(document).on('click', '#listaFornecedoresEdit .list-group-item', function() {
        let idFornecedor = $(this).data('id');
        let nomeFornecedor = $(this).text();
        $('#fornecedorPesquisaEdit').val(nomeFornecedor); // Define o nome no campo de pesquisa
        $('#fornecedor_id_edit').val(idFornecedor); // Define o ID do fornecedor oculto
        $('#listaFornecedoresEdit').hide(); // Esconde a lista
    });
});

// Adicione o seguinte código ao final do arquivo gerenciar.js
document.getElementById('fornecedorPesquisaEdit').addEventListener('input', pesquisarFornecedores);