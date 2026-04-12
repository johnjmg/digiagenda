from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Negocio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='negocio')
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='servicios')
    nombre = models.CharField(max_length=100)
    duracion_minutos = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    categoria = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} - {self.negocio.nombre}"

class Reserva(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmada', 'Confirmada'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    )
    negocio = models.ForeignKey(Negocio, on_delete=models.CASCADE, related_name='reservas')
    servicio = models.ForeignKey(Servicio, on_delete=models.CASCADE)
    cliente_nombre = models.CharField(max_length=100)
    cliente_email = models.EmailField()
    fecha_hora = models.DateTimeField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    token_valoracion = models.CharField(max_length=64, unique=True, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reserva de {self.cliente_nombre} - {self.fecha_hora}"

class Valoracion(models.Model):
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='valoracion')
    puntuacion = models.IntegerField()  # 1 a 5
    comentario = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Valoración {self.puntuacion} para reserva {self.reserva.id}"