document.addEventListener('DOMContentLoaded', function() {
    // Verifica se existem dados de produtos vendidos
    const produtosVendidos = JSON.parse(document.getElementById('grafico-vendas').dataset.produtosVendidos);
    
    if (produtosVendidos.length > 0) {
        // Extrai os nomes dos produtos e as quantidades vendidas
        const labels = produtosVendidos.map(produto => produto[0]);
        const dados = produtosVendidos.map(produto => produto[1]);

        // Inicializa o gráfico no carregamento da página
        createChart();
    }
});

function createChart() {
    const ctx = document.getElementById('grafico-vendas').getContext('2d');
    const selectedProduct = document.getElementById('tipo-roupa').value;

    // Faz uma chamada para a rota que retorna vendas mensais
    fetch(`/vendas_mensais?produto=${selectedProduct}`)
        .then(response => response.json())
        .then(data => {
            if (data.vendas_mensais) {
                // Mapeia os dados para rótulos e quantidades
                const labels = [];
                const quantidadeVendas = [];

                // Mapeia as vendas mensais
                for (let i = 1; i <= 12; i++) {
                    const venda = data.vendas_mensais.find(v => v.mes === i);
                    labels.push(getMonthName(i)); // Função que converte o número do mês para o nome
                    quantidadeVendas.push(venda ? venda.quantidade : 0); // Se não houver venda, coloca 0
                }

                // Verifica se já existe um gráfico no contexto e o remove
                if (window.myChart) {
                    window.myChart.destroy();
                }

                // Cria o gráfico
                window.myChart = new Chart(ctx, {
                    type: 'bar',
                    data: {
                        labels,
                        datasets: [{
                            label: 'Vendas Mensais',
                            data: quantidadeVendas,
                            backgroundColor: 'rgba(255, 99, 132, 0.2)',
                            borderColor: 'rgba(255, 99, 132, 1)',
                            borderWidth: 1
                        }]
                    },
                    options: {
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Meses'
                                }
                            },
                            y: {
                                beginAtZero: true,
                                title: {
                                    display: true,
                                    text: 'Quantidade Vendida'
                                }
                            }
                        }
                    }
                });
            } else {
                console.error('Erro ao carregar dados de vendas mensais:', data.error);
            }
        })
        .catch(error => console.error('Erro:', error));
}

// Função para obter o nome do mês
function getMonthName(month) {
    const monthNames = [
        'Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
    ];
    return monthNames[month - 1]; // Ajusta o índice
}

// Adiciona o listener para o evento de mudança no select
document.getElementById('tipo-roupa').addEventListener('change', createChart);
