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
    filterset_fields = ['genero', 'disponible', 'autor']
    search_fields = ['titulo', 'autor__nombre', 'autor__apellido']
    ordering_fields = ['titulo', 'fecha_publicacion']
    ordering = ['-fecha_publicacion']
    
    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        libros_disponibles = self.queryset.filter(disponible=True)
        serializer = self.get_serializer(libros_disponibles, many=True)
        return Response(serializer.data)
    
    