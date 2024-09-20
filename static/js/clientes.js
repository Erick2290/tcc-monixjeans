document.addEventListener('DOMContentLoaded', function () {
    const formAdicionar = document.getElementById('form-adicionar');
    const formEditar = document.getElementById('form-editar');

    // Adicionando cliente
    formAdicionar.addEventListener('submit', function (event) {
        event.preventDefault();

        const nome = document.getElementById('nome').value;
        const cpf = document.getElementById('cpf').value;
        const cidade = document.getElementById('cidade').value;

        fetch('/clientes/adicionar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nome, cpf, cidade })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                location.reload();  // Atualiza a página
            }
        });
    });

    // Editar cliente
    document.querySelectorAll('.btn-editar').forEach(button => {
        button.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            const nome = this.getAttribute('data-nome');
            const cpf = this.getAttribute('data-cpf');
            const cidade = this.getAttribute('data-cidade');

            document.getElementById('cliente-id').value = id;
            document.getElementById('cliente-nome').value = nome;
            document.getElementById('cliente-cpf').value = cpf;
            document.getElementById('cliente-cidade').value = cidade;
        });
    });

    // Atualiza cliente
    formEditar.addEventListener('submit', function (event) {
        event.preventDefault();
    
        const id = document.getElementById('cliente-id').value;
        const nome = document.getElementById('cliente-nome').value;
        const cpf = document.getElementById('cliente-cpf').value;
        const cidade = document.getElementById('cliente-cidade').value;
    
        console.log({ id, nome, cpf, cidade }); // Adicione isto para verificar os valores
    
        fetch(`/clientes/editar/${id}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ nome, cpf, cidade })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                location.reload();  // Atualiza a página
            }
        })
        .catch(error => {
            alert('Erro ao editar cliente: ' + error.message);
        });
    });
    

    // Pesquisa de clientes
    const formPesquisa = document.querySelector('form[action="/clientes/pesquisar"]');
    formPesquisa.addEventListener('submit', function (event) {
        event.preventDefault();
        const consulta = this.querySelector('input[name="consulta"]').value;

        fetch(`/clientes/pesquisar?consulta=${encodeURIComponent(consulta)}`, {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            const listaClientes = document.getElementById('lista-clientes');
            listaClientes.innerHTML = '';  // Limpa a lista atual

            if (data.success && data.clientes.length > 0) {
                data.clientes.forEach(cliente => {
                    listaClientes.innerHTML += `
                        <li data-id="${cliente.idCliente}">
                            <h3>${cliente.nome}</h3>
                            <p><strong>CPF:</strong> ${cliente.cpf}</p>
                            <p><strong>Cidade:</strong> ${cliente.cidade}</p>
                            <button class="btn btn-sm btn-warning btn-editar" data-bs-toggle="modal" data-bs-target="#editarClienteModal" data-id="${cliente.idCliente}" data-nome="${cliente.nome}" data-cpf="${cliente.cpf}" data-cidade="${cliente.cidade}">Editar</button>
                            <button class="btn btn-sm btn-danger" onclick="deletarCliente(${cliente.idCliente})">Deletar</button>
                        </li>
                    `;
                });
            } else {
                alert('Nenhum cliente encontrado.');
            }
        })
        .catch(error => {
            alert('Erro ao pesquisar clientes: ' + error.message);
        });
    });
});

// Função para deletar cliente
function deletarCliente(id) {
    if (confirm('Você tem certeza que deseja deletar este cliente?')) {
        fetch(`/clientes/deletar/${id}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message);
            if (data.success) {
                location.reload();  // Atualiza a página
            }
        });
    }
}
