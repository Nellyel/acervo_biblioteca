from django.contrib import admin
from .models import Autor, Livro, Exemplar, Membro, Emprestimo, Reserva


class ExemplarAdmin(admin.ModelAdmin):
    readonly_fields = ('disponivel',)

class ReservaAdmin(admin.ModelAdmin):
    list_display = ('membro', 'livro', 'data_reserva', 'atendida', 'posicao_fila')

admin.site.register(Autor)
admin.site.register(Livro)
admin.site.register(Exemplar, ExemplarAdmin)
admin.site.register(Membro)
admin.site.register(Emprestimo)
admin.site.register(Reserva, ReservaAdmin)

