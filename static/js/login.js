document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('#loginForm');

    loginForm.addEventListener('submit', function(event) {
        event.preventDefault();  // Impede o envio padrão do formulário

        const formData = new FormData(loginForm);  // Cria um FormData com os dados do formulário

        // Opções para a requisição fetch
        const requestOptions = {
            method: 'POST',
            body: formData
        };

        // URL para a rota de login
        const loginUrl = '/login';

        // Realiza a requisição fetch para o backend
        fetch(loginUrl, requestOptions)
            .then(response => {
                console.log('Status da resposta:', response.status);
                console.log('Resposta completa:', response);
                if (!response.ok) {
                    throw new Error('Erro ao realizar login. Por favor, tente novamente.');
                }
                return response.json();
            })
            .then(data => {
                console.log('Dados recebidos:', data);
                if (data.success) {
                    // Login bem-sucedido, redireciona para a página inicial
                    window.location.href = '/';
                } else {
                    // Exibe mensagem de erro
                    alert(data.message);
                }
            })
            .catch(error => {
                // Captura e exibe erros de requisição
                console.error('Erro durante a requisição fetch:', error);
                alert('Ocorreu um erro durante o login. Por favor, tente novamente mais tarde.');
            });
    });
});
