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
                document.getElementById('fornecedor_id').value = produto.fornecedor_id;
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
    
});
