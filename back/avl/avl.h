#ifndef AVL_H
#define AVL_H

#include "paciente.h"

typedef struct NoAVL {
    Paciente *paciente;
    int altura;
    struct NoAVL *esq;
    struct NoAVL *dir;
} NoAVL;

int avl_altura(NoAVL *raiz);
int avl_fator_balanceamento(NoAVL *raiz);

NoAVL* avl_rotacao_direita(NoAVL *y);       
NoAVL* avl_rotacao_esquerda(NoAVL *x);      
NoAVL* avl_rotacao_dupla_direita(NoAVL *no); 
NoAVL* avl_rotacao_dupla_esquerda(NoAVL *no); 

NoAVL* avl_inserir(NoAVL *raiz, Paciente *paciente);
void avl_liberar(NoAVL *raiz);

Paciente* avl_buscar_cpf(NoAVL *raiz, const char *cpf, int *comparacoes);
void avl_percurso_em_ordem(NoAVL *raiz);

#endif