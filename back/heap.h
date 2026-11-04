#ifndef HEAP_H
#define HEAP_H

#include "paciente.h"

typedef struct {
    Paciente **dados;
    int tamanho;
    int capacidade;
} Heap;

Heap* heap_criar(int capacidade_inicial);
void heap_liberar(Heap *h);

int heap_inserir(Heap *h, Paciente *p);
Paciente* heap_extrair_max(Heap *h);
Paciente* heap_consultar_topo(const Heap *h);

void heap_construir_bottom_up(Heap *h, Paciente **pool, int total);

int heap_reclassificar(Heap *h, int id_prontuario, int nova_prioridade, const char *nova_classificacao);

int heap_esta_vazio(const Heap *h);
int heap_tamanho(const Heap *h);
int heap_verificar_propriedade(const Heap *h);

#endif
