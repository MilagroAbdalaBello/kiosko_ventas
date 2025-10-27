// KIOSKO_VENTAS/static/js/tpv.js

let carrito = [];
const tablaCarritoBody = document.querySelector('#tabla-carrito tbody');
const totalCarritoElement = document.getElementById('total-carrito');
const productosPanel = document.getElementById('lista-productos');

// Obtenemos el token CSRF del HTML (necesario para AJAX en Django)
const csrftoken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');


// 1. Lógica para manejar el clic en un producto
productosPanel.addEventListener('click', function(e) {
    const card = e.target.closest('.producto-card');
    if (card) {
        const id = card.dataset.id;
        const nombre = card.querySelector('strong').textContent;
        const precio = parseFloat(card.dataset.precio);
        
        agregarProductoAlCarrito(id, nombre, precio);
    }
});

function agregarProductoAlCarrito(id, nombre, precio) {
    // Busca si el producto ya está en el carrito
    const itemExistente = carrito.find(item => item.id === id);

    if (itemExistente) {
        itemExistente.cantidad += 1;
        itemExistente.subtotal = itemExistente.cantidad * itemExistente.precio;
    } else {
        carrito.push({ id: id, nombre: nombre, precio: precio, cantidad: 1, subtotal: precio });
    }
    
    renderizarCarrito();
}

function renderizarCarrito() {
    tablaCarritoBody.innerHTML = ''; 
    let totalGlobal = 0;

    carrito.forEach(item => {
        const fila = tablaCarritoBody.insertRow();
        fila.insertCell(0).textContent = item.nombre;
        fila.insertCell(1).textContent = item.cantidad;
        fila.insertCell(2).textContent = `$${item.subtotal.toFixed(2)}`;
        totalGlobal += item.subtotal;
    });

    totalCarritoElement.textContent = `$${totalGlobal.toFixed(2)}`;
}

// 2. Lógica de Finalizar Venta (Llamada AJAX real a Django)
document.getElementById('btn-finalizar-venta').addEventListener('click', function() {
    if (carrito.length === 0) {
        alert("El carrito está vacío.");
        return;
    }
    
    const totalGlobal = parseFloat(totalCarritoElement.textContent.replace('$', ''));

    fetch('/api/finalizar-venta/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken 
        },
        body: JSON.stringify({ carrito: carrito, total: totalGlobal })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(data.mensaje);
            carrito = [];
            renderizarCarrito();
            // Esto recarga la página para mostrar el stock actualizado
            window.location.reload(); 
        } else {
            alert("Error al finalizar venta: " + data.error);
        }
    })
    .catch(error => {
        console.error('Error de conexión:', error);
        alert('Ocurrió un error de red al contactar al servidor.');
    });
});