from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.RegistroView.as_view(), name='registro'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('negocios/<int:negocio_id>/reservas/', views.ReservaCreateView.as_view(), name='crear_reserva'),
    path('negocios/<int:negocio_id>/servicios/', views.ServiciosPorNegocioView.as_view(), name='servicios_por_negocio'), # Listar servicios de un negocio específico
    path('negocios/<int:pk>/', views.NegocioPublicoView.as_view()), # Detalles públicos de un negocio
    path('negocios/me/', views.MiNegocioView.as_view(), name='mi_negocio'),
    path('servicios/', views.ServicioListCreateView.as_view(), name='servicios'),
    path('servicios/<int:pk>/', views.ServicioRetrieveUpdateDestroyView.as_view(), name='servicio_detail'),
    path('reservas/', views.ReservaListView.as_view(), name='reservas_list'),
    path('negocios/<int:negocio_id>/reservas/', views.ReservaCreateView.as_view(), name='crear_reserva'),
    path('reservas/<int:reserva_id>/completar/', views.CompletarReservaView.as_view(), name='completar_reserva'),
    path('valoraciones/', views.ValoracionCreateView.as_view(), name='crear_valoracion'),
    path('negocios/<int:negocio_id>/valoraciones/', views.ValoracionesNegocioView.as_view(), name='valoraciones_negocio'),
]