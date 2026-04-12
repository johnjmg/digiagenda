from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Negocio, Servicio, Reserva, Valoracion

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class NegocioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class Meta:
        model = Negocio
        fields = '__all__'

class ServicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicio
        fields = '__all__'

class ReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reserva
        fields = '__all__'
        read_only_fields = ('token_valoracion',)

class ReservaCreateSerializer(serializers.ModelSerializer):
    servicio_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Reserva
        fields = ['servicio_id', 'cliente_nombre', 'cliente_email', 'fecha_hora']

    def create(self, validated_data):
        servicio_id = validated_data.pop('servicio_id')
        negocio_id = self.context['negocio_id']  # lo pasamos desde la vista
        servicio = Servicio.objects.get(id=servicio_id)
        reserva = Reserva.objects.create(
            negocio_id=negocio_id,
            servicio=servicio,
            **validated_data
        )
        return reserva
# Serializer para mostrar valoraciones (sin token)
class ValoracionSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source='reserva.cliente_nombre', read_only=True)
    servicio_nombre = serializers.CharField(source='reserva.servicio.nombre', read_only=True)

    class Meta:
        model = Valoracion
        fields = ['id', 'reserva', 'puntuacion', 'comentario', 'fecha', 'cliente_nombre', 'servicio_nombre']

# Serializers para registro y login
class RegistroSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nombre = serializers.CharField(max_length=100)
    direccion = serializers.CharField(required=False, allow_blank=True)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

# Serializer para crear valoraciones (requiere token de reserva)
class ValoracionCreateSerializer(serializers.Serializer):
    token = serializers.CharField()
    puntuacion = serializers.IntegerField(min_value=1, max_value=5)
    comentario = serializers.CharField(required=False, allow_blank=True)

