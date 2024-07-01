document.addEventListener('DOMContentLoaded', function() {
// Función para procesar datos y actualizar gráficas
    function actualizarGrafica(idCanvas, datasets, opciones) {
    var ctx = document.getElementById(idCanvas).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: datasets[0].datos.map(report => `${report.nombre_vaca}`),  // Usar las etiquetas de la primera serie de datos
            datasets: datasets.map(dataset => ({
                label: dataset.label,
                backgroundColor: dataset.backgroundColor,
                borderColor: dataset.borderColor,
                borderWidth: 1,
                data: dataset.datos.map(report => report[dataset.campoValor])
            }))
        },
        options: opciones
    });
}

// Configuración de las opciones de las gráficas
var opcionesGrafica = {
    scales: {
        y: {
            beginAtZero: true
        },
        x: {
            ticks:
            {
                font: {
                    size:8
                }
            }
        }
    },
};

// Realiza una solicitud AJAX para obtener datos de la API
$.ajax({
    url: '/monitor/datos/', // Reemplaza con la URL correcta de tu API
    method: 'GET',
    success: function(response) {

        // Filtrar los últimos 10 reportes
        var ultimosReportes = response.reportes.slice(-10);

          // Definir los datasets para la gráfica combinada
          var datasets = [
            {
                label: 'Temperatura (°C)',
                backgroundColor: 'rgba(2, 132, 22, 0.9)',
                borderColor: 'rgb(6, 252, 18)',
                datos: ultimosReportes,
                campoValor: 'temperatura'
            },
            {
                label: 'Frecuencia Cardiaca',
                backgroundColor: '#f52828',
                borderColor: 'rgb(134, 7, 11)',
                datos: ultimosReportes,
                campoValor: 'pulsaciones'
            }
        ];

        // Actualiza la gráfica de temperatura
             // Actualizar la gráfica combinada
             actualizarGrafica('temperaturaHumedadCardiacaChart', datasets, opcionesGrafica);
    },
    error: function(error) {
        console.error('Error al obtener datos de la API:', error);
    }
});
});
