from django.urls import path
from . import views

urlpatterns = [
    path('livros/', views.lista_livros, name='lista'),
    path('livros/novo/', views.novo_livro, name='novo_livro'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/csv/', views.exportar_csv, name='exportar_csv'),
]

