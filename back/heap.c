#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "heap.h"

static int tem_maior_prioridade(const Paciente *a, const Paciente *b) {
    if (!a) return 0;
    if (!b) return 1;

    if (a->prioridade != b->prioridade) {
        return a->prioridade > b->prioridade;
    }
    return a->horario_chegada < b->horario_chegada;
}

static void trocar(Paciente **a, Paciente **b) {
    Paciente *temp = *a;
    *a = *b;
    *b = temp;
}

static int garantir_capacidade(Heap *h) {
    if (h->tamanho < h->capacidade) {
        return 1;
    }

    int nova_capacidade = (h->capacidade <= 0) ? 1000 : h->capacidade * 2;
    Paciente **novo_vetor = (Paciente**) realloc(h->dados, sizeof(Paciente*) * nova_capacidade);
    if (!novo_vetor) {
        fprintf(stderr, "Erro de memoria: Falha ao redimensionar Heap para %d elementos.\n", nova_capacidade);
        return 0;
    }

    h->dados = novo_vetor;
    h->capacidade = nova_capacidade;
    return 1;
}

static void subir_heap(Heap *h, int i) {
    while (i > 0) {
        int pai = (i - 1) / 2;
        if (tem_maior_prioridade(h->dados[i], h->dados[pai])) {
            trocar(&h->dados[i], &h->dados[pai]);
            i = pai;
        } else {
            break;
        }
    }
}

static void descer_heap(Heap *h, int i) {
    while (1) {
        int esq = 2 * i + 1;
        int dir = 2 * i + 2;
        int maior = i;

        if (esq < h->tamanho && tem_maior_prioridade(h->dados[esq], h->dados[maior])) {
            maior = esq;
        }
        if (dir < h->tamanho && tem_maior_prioridade(h->dados[dir], h->dados[maior])) {
            maior = dir;
        }

        if (maior != i) {
            trocar(&h->dados[i], &h->dados[maior]);
            i = maior;
        } else {
            break;
        }
    }
}

Heap* heap_criar(int capacidade_inicial) {
    if (capacidade_inicial <= 0) {
        capacidade_inicial = 1000;
    }

    Heap *h = (Heap*) malloc(sizeof(Heap));
    if (!h) {
        fprintf(stderr, "Erro ao alocar estrutura Heap.\n");
        return NULL;
    }

    h->dados = (Paciente**) malloc(sizeof(Paciente*) * capacidade_inicial);
    if (!h->dados) {
        fprintf(stderr, "Erro ao alocar vetor de dados do Heap.\n");
        free(h);
        return NULL;
    }

    h->tamanho = 0;
    h->capacidade = capacidade_inicial;
    return h;
}

void heap_liberar(Heap *h) {
    if (!h) return;
    if (h->dados) {
        free(h->dados);
    }
    free(h);
}

int heap_inserir(Heap *h, Paciente *p) {
    if (!h || !p) return 0;

    if (!garantir_capacidade(h)) {
        return 0;
    }

    h->dados[h->tamanho] = p;
    subir_heap(h, h->tamanho);
    h->tamanho++;
    return 1;
}

Paciente* heap_extrair_max(Heap *h) {
    if (!h || h->tamanho == 0) {
        return NULL;
    }

    Paciente *max = h->dados[0];
    h->tamanho--;

    if (h->tamanho > 0) {
        h->dados[0] = h->dados[h->tamanho];
        descer_heap(h, 0);
    }

    strncpy(max->status, "Em Atendimento", TAM_STATUS - 1);
    max->status[TAM_STATUS - 1] = '\0';

    return max;
}

Paciente* heap_consultar_topo(const Heap *h) {
    if (!h || h->tamanho == 0) {
        return NULL;
    }
    return h->dados[0];
}

void heap_construir_bottom_up(Heap *h, Paciente **pool, int total) {
    if (!h || !pool || total <= 0) return;

    if (total > h->capacidade) {
        Paciente **novo_vetor = (Paciente**) realloc(h->dados, sizeof(Paciente*) * total);
        if (!novo_vetor) {
            fprintf(stderr, "Erro ao redimensionar Heap para construcao Bottom-Up.\n");
            return;
        }
        h->dados = novo_vetor;
        h->capacidade = total;
    }

    for (int i = 0; i < total; i++) {
        h->dados[i] = pool[i];
    }
    h->tamanho = total;

    for (int i = (total / 2) - 1; i >= 0; i--) {
        descer_heap(h, i);
    }
}

int heap_reclassificar(Heap *h, int id_prontuario, int nova_prioridade, const char *nova_classificacao) {
    if (!h || h->tamanho == 0) return 0;

    int idx = -1;
    for (int i = 0; i < h->tamanho; i++) {
        if (h->dados[i]->id_prontuario == id_prontuario) {
            idx = i;
            break;
        }
    }

    if (idx == -1) {
        return 0;
    }

    int antiga_prioridade = h->dados[idx]->prioridade;
    h->dados[idx]->prioridade = nova_prioridade;

    if (nova_classificacao) {
        strncpy(h->dados[idx]->classificacao, nova_classificacao, TAM_CLASSIFICACAO - 1);
        h->dados[idx]->classificacao[TAM_CLASSIFICACAO - 1] = '\0';
    }

    if (nova_prioridade > antiga_prioridade) {
        subir_heap(h, idx);
    } else if (nova_prioridade < antiga_prioridade) {
        descer_heap(h, idx);
    }

    return 1;
}

int heap_esta_vazio(const Heap *h) {
    return (!h || h->tamanho == 0);
}

int heap_tamanho(const Heap *h) {
    return h ? h->tamanho : 0;
}

int heap_verificar_propriedade(const Heap *h) {
    if (!h || h->tamanho <= 1) return 1;

    for (int i = 0; i < h->tamanho / 2; i++) {
        int esq = 2 * i + 1;
        int dir = 2 * i + 2;

        if (esq < h->tamanho && tem_maior_prioridade(h->dados[esq], h->dados[i])) {
            return 0;
        }
        if (dir < h->tamanho && tem_maior_prioridade(h->dados[dir], h->dados[i])) {
            return 0;
        }
    }

    return 1;
}
