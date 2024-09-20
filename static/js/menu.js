document.addEventListener('DOMContentLoaded', function() {
    const loginLink = document.getElementById('loginLink');

    loginLink.addEventListener('click', function() {
        window.location.href = "/login";
    });

    const controladorEstoqueButton = document.querySelector('.funcionalidades-box:nth-child(1)');
    controladorEstoqueButton.addEventListener('click', function() {
        window.location.href = "/gerenciar";
    });

    const fornecedoresButton = document.querySelector('.funcionalidades-box:nth-child(2)');
    fornecedoresButton.addEventListener('click', function() {
        window.location.href = "/fornecedores";
    });

    // Seletor do botão "Clientes"
    const clientesButton = document.querySelector('.funcionalidades-box:nth-child(3)');
    clientesButton.addEventListener('click', function() {
        window.location.href = "/clientes";
    });

    const extratoButton = document.querySelector('.funcionalidades-box:nth-child(4)');
    extratoButton.addEventListener('click', function() {
        window.location.href = "/extrato";
    });

    const addVendaButton = document.querySelector('.funcionalidades-box:nth-child(5)');
    addVendaButton.addEventListener('click', function() {
        window.location.href = "/addvenda";
    });

    const logoutButton = document.getElementById('logoutButton');
    logoutButton.addEventListener('click', function() {
        fetch('/logout', { method: 'GET' })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            }
        });
    });

    const deleteAccountButton = document.getElementById('deleteAccountButton');
    deleteAccountButton.addEventListener('click', function() {
        if (confirm('Você tem certeza que deseja apagar sua conta?')) {
            fetch('/delete_account', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Conta apagada com sucesso.');
                    window.location.href = "/login";
                } else {
                    alert('Erro ao apagar a conta: ' + data.message);
                }
            });
        }
    });

    const editAccountButton = document.getElementById('editAccountButton');
    editAccountButton.addEventListener('click', function() {
        const senha_antiga = prompt('Digite sua senha antiga:');
        const nova_senha = prompt('Digite sua nova senha:');
        const novo_nome = prompt('Digite seu novo nome:');
        const novo_cpf = prompt('Digite seu novo CPF:');

        if (senha_antiga && nova_senha && novo_nome && novo_cpf) {
            fetch('/edit_account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ senha_antiga, nova_senha, novo_nome, novo_cpf })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Conta editada com sucesso.');
                    window.location.href = "/login";
                } else {
                    alert('Erro ao editar a conta: ' + data.message);
                }
            });
        } else {
            alert('Por favor, preencha todos os campos.');
        }
    });
});
