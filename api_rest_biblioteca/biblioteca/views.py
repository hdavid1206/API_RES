from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Autor, Libro, Prestamo
from .serializers import AutorSerializer, LibroSerializer, PrestamoSerializer

class AutorViewSet(viewsets.ModelViewSet):
    queryset = Autor.objects.all()
    serializer_class = AutorSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['nacionalidad']
    search_fields = ['nombre', 'apellido']
    ordering_fields = ['nombre', 'fecha_nacimiento']
    ordering = ['apellido', 'nombre']

class LibroViewSet(viewsets.ModelViewSet):
    queryset = Libro.objects.all()
    serializer_class = LibroSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['genero', 'disponible', 'Autor']  # Cambiado a 'Autor' con mayúscula
    search_fields = ['titulo', 'Autor__nombre', 'Autor__apellido']  # Cambiado a 'Autor' con mayúscula
    ordering_fields = ['titulo', 'fecha_publication']  # Cambiado a 'fecha_publication'
    ordering = ['-fecha_publication']  # Cambiado a 'fecha_publication'
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        libros_disponibles = self.queryset.filter(disponible=True)
        serializer = self.get_serializer(libros_disponibles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])  # Cambiado a detail=True
    def prestar(self, request, pk=None):
        libro = self.get_object()
        if not libro.disponible:
            return Response(
                {'error': 'Libro no disponible'}, 
                status=status.HTTP_400_BAD_REQUEST
                )
            
        prestamo = Prestamo.objects.create(
            libro=libro,
            usuario=request.user
            )
        libro.disponible = False
        libro.save()
        
        return Response({'mensaje': f'Libro "{libro.titulo}" prestado exitosamente'})

class PrestamoViewSet(viewsets.ModelViewSet):
    serializer_class = PrestamoSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['devuelto','usuario']
    ordering = ['-fecha_prestamo']
    
    def get_queryset(self):
        # Para pruebas, permitir ver todos los préstamos
        # En producción, descomenta las líneas de abajo para filtrar por usuario
        return Prestamo.objects.all()
        
        # if self.request.user and self.request.user.is_authenticated:
        #     if self.request.user.is_staff:
        #         return Prestamo.objects.all()
        #     return Prestamo.objects.filter(usuario=self.request.user)
        # return Prestamo.objects.none()
    
    @action(detail=True, methods=['post'])
    def devolver(self, request, pk=None):
        prestamo = self.get_object()
        if prestamo.devuelto:
            return Response(
                {'error': 'Este libro ya fue devuelto'}, 
                status=status.HTTP_400_BAD_REQUEST
                )
            
        prestamo.devuelto = True
        prestamo.libro.disponible = True
        prestamo.save()
        prestamo.libro.save()
        
        return Response({'mensaje': 'Libro devuelto exitosamente'})