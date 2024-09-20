// JavaScript para enviar requisições AJAX
    
// Função para adicionar fornecedor
document.getElementById('form-adicionar').addEventListener('submit', function(event) {
    event.preventDefault();
    
    let nome = document.getElementById('nome').value;
    let endereco = document.getElementById('endereco').value;
    let email = document.getElementById('email').value;
    let produtos = document.getElementById('produtos').value;

    fetch('/fornecedores/adicionar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nome: nome,
            endereco: endereco,
            email: email,
            produtos: produtos
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recarregar a página ou atualizar a lista de fornecedores
            window.location.reload();
        } else {
            alert('Erro ao adicionar fornecedor: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});

// Função para editar fornecedor
document.querySelectorAll('.btn-editar').forEach(button => {
    button.addEventListener('click', function() {
        const fornecedorId = this.getAttribute('data-id');
        const nome = this.getAttribute('data-nome');
        const endereco = this.getAttribute('data-endereco');
        const email = this.getAttribute('data-email');
        const produtos = this.getAttribute('data-produtos');

        // Preencha os campos do modal com os dados do fornecedor
        document.getElementById('fornecedor-id').value = fornecedorId;
        document.getElementById('fornecedor-nome').value = nome;
        document.getElementById('fornecedor-endereco').value = endereco;
        document.getElementById('fornecedor-email').value = email;
        document.getElementById('fornecedor-produtos').value = produtos;
    });
});

// Função para deletar fornecedor
document.querySelectorAll('.btn-deletar').forEach(button => {
    button.addEventListener('click', function() {
        let fornecedorId = this.parentElement.getAttribute('data-id');
        
        fetch(`/fornecedores/deletar/${fornecedorId}`, {
            method: 'POST',
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recarregar a página ou atualizar a lista de fornecedores
                window.location.reload();
            } else {
                alert('Erro ao deletar fornecedor: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    });
});

// Adicione um evento de envio ao formulário de edição
document.getElementById('form-editar').addEventListener('submit', function(event) {
    event.preventDefault();

    const fornecedorId = document.getElementById('fornecedor-id').value;
    const nome = document.getElementById('fornecedor-nome').value;
    const endereco = document.getElementById('fornecedor-endereco').value;
    const email = document.getElementById('fornecedor-email').value;
    const produtos = document.getElementById('fornecedor-produtos').value;

    // Faça uma requisição AJAX para atualizar o fornecedor
    fetch(`/fornecedores/editar/${fornecedorId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            nome: nome,
            endereco: endereco,
            email: email,
            produtos: produtos
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Recarregar a página ou atualizar a lista de fornecedores
            window.location.reload();
        } else {
            alert('Erro ao editar fornecedor: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
});


