from django.urls import path
from . import api_views as views

urlpatterns = [
    path('livros/', views.LivroListCreate.as_view()),
    path('livros/<int:pk>/', views.LivroDetail.as_view()),

    path('autores/', views.AutorListCreate.as_view()),
    path('autores/<int:pk>/', views.AutorDetail.as_view()),

    path('exemplares/', views.ExemplarListCreate.as_view()),
    path('exemplares/<int:pk>/', views.ExemplarDetail.as_view()),

    path('membros/', views.MembroListCreate.as_view()),
    path('membros/<int:pk>/', views.MembroDetail.as_view()),

    path('emprestimos/', views.EmprestimoListCreate.as_view()),
    path('emprestimos/<int:pk>/', views.EmprestimoDetail.as_view()),

    path('reservas/', views.ReservaListCreate.as_view()),
    path('reservas/<int:pk>/', views.ReservaDetail.as_view()),
]