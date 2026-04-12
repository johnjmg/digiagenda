from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.db import transaction
import secrets
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Negocio, Servicio, Reserva, Valoracion
from .serializers import (
    NegocioSerializer, ServicioSerializer, ValoracionSerializer, RegistroSerializer, LoginSerializer, ValoracionCreateSerializer, ReservaCreateSerializer, ReservaSerializer
)

# ====================
# Registro de negocio (crea usuario + negocio)
# ====================
@swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'email': openapi.Schema(type=openapi.TYPE_STRING, description='Correo electrónico (usado como username)'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Contraseña'),
            'nombre': openapi.Schema(type=openapi.TYPE_STRING, description='Nombre del negocio'),
            'direccion': openapi.Schema(type=openapi.TYPE_STRING, description='Dirección (opcional)'),
        },
        required=['email', 'password', 'nombre']
    )
)
class RegistroView(generics.CreateAPIView):
    serializer_class = RegistroSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data['email']
        email = data['email']
        password = data['password']
        nombre = data['nombre']
        direccion = data.get('direccion', '')

        if User.objects.filter(username=username).exists():
            return Response({'detail': 'El email ya está registrado'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            negocio = Negocio.objects.create(user=user, nombre=nombre, direccion=direccion)
        return Response(NegocioSerializer(negocio).data, status=status.HTTP_201_CREATED)


class LoginView(generics.CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        from django.contrib.auth import authenticate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        user = authenticate(username=email, password=password)
        if not user:
            return Response({'detail': 'Email o contraseña incorrectos'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })


# ====================
# Obtener el negocio del usuario autenticado
# ====================
class MiNegocioView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        negocio = Negocio.objects.get(user=request.user)
        return Response(NegocioSerializer(negocio).data)


# ====================
# Servicios (CRUD) - solo para el negocio autenticado
# ====================
class ServicioListCreateView(generics.ListCreateAPIView):
    serializer_class = ServicioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Servicio.objects.filter(negocio__user=self.request.user)

    def perform_create(self, serializer):
        negocio = Negocio.objects.get(user=self.request.user)
        serializer.save(negocio=negocio)


class ServicioRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ServicioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Servicio.objects.filter(negocio__user=self.request.user)


# ====================
# Reservas públicas (cualquiera puede crear)
# ====================
@swagger_auto_schema(
    request_body=ReservaSerializer,
    manual_parameters=[
        openapi.Parameter('negocio_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='ID del negocio')
    ]
)
class ReservaCreateView(generics.CreateAPIView):
    serializer_class = ReservaCreateSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['negocio_id'] = self.kwargs['negocio_id']
        return context

    def perform_create(self, serializer):
        serializer.save()  # el create del serializer ya maneja todo


# ====================
# Listar reservas del negocio autenticado
# ====================
class ReservaListView(generics.ListAPIView):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reserva.objects.filter(negocio__user=self.request.user)


# ====================
# Completar reserva y generar token de valoración
# ====================
@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter('reserva_id', openapi.IN_PATH, type=openapi.TYPE_INTEGER, description='ID de la reserva')
    ]
)
class CompletarReservaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, reserva_id):
        try:
            reserva = Reserva.objects.get(id=reserva_id, negocio__user=request.user)
        except Reserva.DoesNotExist:
            return Response({'detail': 'Reserva no encontrada'}, status=status.HTTP_404_NOT_FOUND)
        if reserva.estado == 'completada':
            return Response({'detail': 'Ya completada'}, status=status.HTTP_400_BAD_REQUEST)
        token = secrets.token_hex(32)
        reserva.token_valoracion = token
        reserva.estado = 'completada'
        reserva.save()
        return Response(ReservaSerializer(reserva).data)


# ====================
# Crear valoración (pública, con token)
# ====================
@swagger_auto_schema(
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token de valoración'),
            'puntuacion': openapi.Schema(type=openapi.TYPE_INTEGER, description='Puntuación de 1 a 5'),
            'comentario': openapi.Schema(type=openapi.TYPE_STRING, description='Comentario (opcional)'),
        },
        required=['token', 'puntuacion']
    )
)
class ValoracionCreateView(generics.CreateAPIView):
    serializer_class = ValoracionCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data['token']
        puntuacion = serializer.validated_data['puntuacion']
        comentario = serializer.validated_data.get('comentario', '')

        try:
            reserva = Reserva.objects.get(token_valoracion=token, estado='completada')
        except Reserva.DoesNotExist:
            return Response({'detail': 'Token inválido'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(reserva, 'valoracion'):
            return Response({'detail': 'Esta reserva ya fue valorada'}, status=status.HTTP_400_BAD_REQUEST)

        valoracion = Valoracion.objects.create(reserva=reserva, puntuacion=puntuacion, comentario=comentario)
        return Response(ValoracionSerializer(valoracion).data, status=status.HTTP_201_CREATED)


# ====================
# Listar valoraciones públicas de un negocio
# ====================
class ValoracionesNegocioView(generics.ListAPIView):
    serializer_class = ValoracionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        negocio_id = self.kwargs['negocio_id']
        return Valoracion.objects.filter(reserva__negocio_id=negocio_id)


class NegocioPublicoView(generics.RetrieveAPIView): # Detalles públicos de un negocio (sin datos sensibles)
    queryset = Negocio.objects.all()
    serializer_class = NegocioSerializer
    permission_classes = [permissions.AllowAny]

class ServiciosPorNegocioView(generics.ListAPIView):# Listar servicios de un negocio específico (público)
    serializer_class = ServicioSerializer
    permission_classes = [permissions.AllowAny]  # Público

    def get_queryset(self):
        negocio_id = self.kwargs['negocio_id']
        return Servicio.objects.filter(negocio_id=negocio_id)