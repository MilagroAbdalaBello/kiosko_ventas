# ventas/urls.py
# ventas/urls.py

from django.urls import path
from . import views

urlpatterns = [ 
    path("tpv/", views.tpv_view, name="tpv"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("api/finalizar-venta/", views.finalizar_venta_ajax, name="finalizar_venta_ajax"),
    path("registro/empleado/", views.registro_empleado, name="registro_empleado"), 
]