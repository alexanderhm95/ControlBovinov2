console.log('Inicio de la función actualizarDatos');

document.addEventListener('DOMContentLoaded', function() {
    function actualizarDatos(contenedorId, collarId) {
        //se extrae el numero desde contenedorId ya que llega como relojDatos1, relojDatos2, etc.
        var collarNum = contenedorId.match(/\d+/)[0];
        //Se extrae el número desde contenedorId ya que llega como relojDatos1, relojDatos2, etc.
        
        fetch('/ultimo/registro/' + collarId)
            .then(response => {
                if (response.status !== 200) {
                    throw new Error('Error al obtener datos');
                }
                return response.json();
            })
            .then(data => {
                if (data.error) {
                    document.getElementById(contenedorId).innerHTML = 
                    `Collar ${collarId} <br><br><br><br>
                    <i class="bi bi-exclamation-triangle"></i> Datos no disponibles`;
                } else {
                    // Actualiza el contenido del reloj
                    document.getElementById(contenedorId).innerHTML = 
                    `Collar ${collarId} <br> 
                    Nombre: ${data.nombre_vaca || ''} <br>
                    Temperatura: ${data.temperatura || ''}°C <br> 
                    Pulsaciones: ${data.pulsaciones || ''} bpm <br> 
                    Fecha control: ${data.fecha_lectura || ''} ${data.hora_lectura || ''}`;
                }
            })
            .catch(error => {
                document.getElementById(contenedorId).innerHTML = 
                `Collar ${collarId} <br><br><br><br>
                <i class="bi bi-exclamation-triangle"></i> Datos no disponibles`;
            });
    }

    // Llama a actualizarDatos cada 5 segundos
    setInterval(() => {
        actualizarDatos(collarId,collarNum);
    }, 5000); // Asegúrate de usar 5000 ms (5 segundos)
});