# ventas/views.py

# Ahora importamos 'render' (para usar plantillas) y el modelo 'Producto'
from django.shortcuts import render 
from .models import Producto, Categoria, Venta, DetalleVenta # <-- Importa tu modelo
from django.http import JsonResponse # <-- ¡Importa esto!
import json
from django.views.decorators.http import require_POST # <-- ¡Importa esto!
from django.views.decorators.csrf import csrf_exempt # <-- ¡Importa esto temporalmente!
from decimal import Decimal # Para manejo preciso de dinero
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect # Asegúrate de tener redirect
from django.contrib.auth.forms import UserCreationForm # <-- Importa el formulario de Django
from django.contrib.auth.models import Group # <-- Importa el modelo de Grupos (Roles)
from django.contrib.auth.decorators import login_required, user_passes_test # <-- Importa user_passes_test

def index(request):
    # 1. Trae todos los productos de la base de datos MySQL (los que cargaste en el Admin)
    todos_los_productos = Producto.objects.all().order_by('nombre')
    
    # 2. Crea un diccionario para enviar los datos a la plantilla (Contexto)
    contexto = {
        'productos': todos_los_productos,
        'titulo': 'Inventario del Kiosco'
    }
    
    # 3. Usa 'render' para cargar el template y pasarle el contexto
    return render(request, 'ventas/vistaprincipal.html', contexto)
# Función de prueba: Solo permite el acceso si el usuario es 'Jefe' o 'Empleado'
def es_personal(user):
    return user.groups.filter(name__in=['Jefe', 'Empleado']).exists()
@user_passes_test(es_personal) # <-- ¡Aplica la restricción por rol!

def tpv_view(request):
    """
    Vista principal del Terminal Punto de Venta (TPV).
    Carga todos los productos y categorías.    
    """
    """
    Vista principal del Terminal Punto de Venta (TPV).
    Solo accesible para usuarios con roles 'Jefe' o 'Empleado'.
    """
    # Traemos todas las categorías para mostrarlas como botones/filtros
    categorias = Categoria.objects.all().order_by('nombre')
    
    # Traemos todos los productos (se filtrarán en el frontend)
    productos = Producto.objects.filter(stock__gt=0).order_by('nombre') 
    # Usamos filter(stock__gt=0) para solo mostrar productos con stock > 0
    
    contexto = {
        'categorias': categorias,
        'productos': productos,
        'titulo': 'Terminal Punto de Venta'
    }
    
    # Usaremos una plantilla HTML llamada 'tpv.html'
    return render(request, 'ventas/tpv.html', contexto)

# Usamos @require_POST para asegurar que solo se accede con POST
# Usamos @csrf_exempt solo para desarrollo; en producción, usarías un decorador más seguro.
@require_POST
@csrf_exempt 
def finalizar_venta_ajax(request):
    """Procesa los datos de venta enviados por AJAX."""
    
    try:
        # 1. Leer los datos JSON
        datos_recibidos = json.loads(request.body)
        carrito_data = datos_recibidos.get('carrito')
        total_global = Decimal(datos_recibidos.get('total', '0.00'))

        if not carrito_data:
            return JsonResponse({'success': False, 'error': 'El carrito está vacío.'}, status=400)

        # 2. Crear la Venta (Recibo)
        nueva_venta = Venta.objects.create(total_venta=total_global)
        
        # 3. Procesar los ítems del carrito y actualizar stock
        for item in carrito_data:
            producto_id = item['id']
            cantidad = item['cantidad']
            precio = Decimal(item['precio']) # Precio unitario al momento de la venta
            
            # Buscar el producto y el stock
            producto = Producto.objects.get(id=producto_id)
            
            # 4. Crear el DetalleVenta (Ítem del Recibo)
            DetalleVenta.objects.create(
                venta=nueva_venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=precio,
                subtotal=precio * cantidad
            )
            
            # 5. Actualizar Stock
            producto.stock -= cantidad
            producto.save()

        # 6. Éxito
        return JsonResponse({'success': True, 'mensaje': f'Venta #{nueva_venta.id} registrada con éxito.'})

    except Producto.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Producto no encontrado.'}, status=404)
    except Exception as e:
        # Esto captura cualquier otro error (ej: stock insuficiente, error de base de datos)
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

# Ya puedes eliminar la importación 'from django.http import HttpResponse' si solo usas esta vista.

@login_required # <-- ¡Solo usuarios logueados pueden acceder!
def dashboard(request):
    """Página de inicio después del login. Servirá como el menú principal."""
    contexto = {
        'user': request.user,
        'es_jefe': request.user.groups.filter(name='Jefe').exists(),
        'es_empleado': request.user.groups.filter(name='Empleado').exists(),
    }
    return render(request, 'ventas/dashboard.html', contexto)

def registro_empleado(request):
    """Permite que un nuevo empleado se registre y asigna el rol 'Empleado'."""
    if request.method == 'POST':
        # 1. Procesa el formulario enviado
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # Guarda el usuario en la base de datos
            
            # 2. Asignar el rol 'Empleado' automáticamente
            try:
                # Busca el grupo 'Empleado' que creaste en el Admin
                grupo_empleado = Group.objects.get(name='Empleado')
                user.groups.add(grupo_empleado) # Asigna el grupo al nuevo usuario
            except Group.DoesNotExist:
                # Esto es un error de configuración; debería existir
                print("ADVERTENCIA: El grupo 'Empleado' no existe en la base de datos.")

            # 3. Redireccionar al login después de un registro exitoso
            return redirect('login') 
            
    else:
        # Crea un formulario vacío para mostrar
        form = UserCreationForm()
        
    contexto = {'form': form}
    return render(request, 'ventas/registro_empleado.html', contexto)

# VISTA NUEVA: REGISTROS DE VENTA (Reportes)
@login_required
def reportes(request):
    """Muestra el registro de todas las ventas para el Jefe."""
    
    # 1. Verificar Rol (Medida de Seguridad Adicional)
    if not request.user.groups.filter(name='Jefe').exists():
        # Redirigir o mostrar un mensaje de error si no es Jefe
        return render(request, 'ventas/dashboard.html', {'error': 'Acceso Denegado'})

    # 2. Obtener todas las ventas
    # Seleccionamos las ventas y precargamos el usuario que hizo la venta para evitar consultas lentas.
    ventas = Venta.objects.select_related('empleado').order_by('-fecha') 
    
    contexto = {
        'titulo': 'Registro de Ventas',
        'ventas': ventas,
    }
    return render(request, 'ventas/reportes.html', contexto)

# VISTA NUEVA: APERTURA Y CIERRE DE CAJA
@login_required
def caja(request):
    # Aquí irá la lógica de manejo de caja
    return render(request, 'ventas/caja.html', {'titulo': 'Apertura y Cierre de Caja'})