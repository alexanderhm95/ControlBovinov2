document.addEventListener('DOMContentLoaded', function() {
// Función para procesar datos y actualizar gráficas
function actualizarGrafica(idCanvas, label, backgroundColor, borderColor, datos, campoValor, opciones) {
    var ctx = document.getElementById(idCanvas).getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: datos.map(report => `${report.fecha_creacion}`),  // Combina fecha y hora
            datasets: [{
                label: label,
                backgroundColor: backgroundColor,
                borderColor: borderColor,
                borderWidth: 1,
                data: datos.map(report => report[campoValor])
            }]
        },
        options: opciones
    });
}

// Configuración de las opciones de las gráficas
var opcionesGrafica = {
    scales: {
        y: {
            beginAtZero: true
        }
    }
};

// Realiza una solicitud AJAX para obtener datos de la API
$.ajax({
    url: '/monitor/datos/', // Reemplaza con la URL correcta de tu API
    method: 'GET',
    success: function(response) {

        // Filtrar los últimos 10 reportes
        var ultimosReportes = response.reportes.slice(-10);

        // Actualiza la gráfica de temperatura
        actualizarGrafica('temperaturaHumedadChart', 'Temperatura (°C)', 'rgba(255, 237, 0, 0.53)', 'rgba(255, 237, 0, 0.53)', ultimosReportes, 'temperatura', opcionesGrafica);

        // Actualiza la gráfica de pulsaciones
        actualizarGrafica('sensorCardiacoChart1', 'Frecuencia Cardiaca', 'rgba(255, 99, 132, 0.2)', 'rgba(255, 99, 132, 1)', ultimosReportes, 'pulsaciones', opcionesGrafica);
    },
    error: function(error) {
        console.error('Error al obtener datos de la API:', error);
    }
});
});
