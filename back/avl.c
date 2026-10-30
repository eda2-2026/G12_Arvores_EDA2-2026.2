#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "avl.h"

static int max(int a, int b) {
    return (a > b) ? a : b;
}

int avl_altura(NoAVL *raiz) {
    if (!raiz) return 0;
    return raiz->altura;
}

int avl_fator_balanceamento(NoAVL *raiz) {
    if (!raiz) return 0;
    return avl_altura(raiz->esq) - avl_altura(raiz->dir);
}

//rotação Simples à Direita
//filho esquerdo 'x' sobe e 'y' torna-se filho direito de 'x'
NoAVL* avl_rotacao_direita(NoAVL *y) {
    NoAVL *x = y->esq;
    NoAVL *T2 = x->dir;

    x->dir = y;
    y->esq = T2;

    y->altura = max(avl_altura(y->esq), avl_altura(y->dir)) + 1;
    x->altura = max(avl_altura(x->esq), avl_altura(x->dir)) + 1;

    return x;
}

//rotação Simples à Esquerda
//filho direito 'y' sobe e 'x' torna-se filho esquerdo de 'y'
NoAVL* avl_rotacao_esquerda(NoAVL *x) {
    NoAVL *y = x->dir;
    NoAVL *T2 = y->esq;

    y->esq = x;
    x->dir = T2;

    x->altura = max(avl_altura(x->esq), avl_altura(x->dir)) + 1;
    y->altura = max(avl_altura(y->esq), avl_altura(y->dir)) + 1;

    return y;
}

// Rotação Dupla à Direita
// rotaciona o filho esquerdo para a esquerda, depois o nó para a direita
NoAVL* avl_rotacao_dupla_direita(NoAVL *no) {
    no->esq = avl_rotacao_esquerda(no->esq);
    return avl_rotacao_direita(no);
}

// Rotação Dupla à Esquerda 
// rotaciona o filho direito para a direita, depois o nó para a esquerda
NoAVL* avl_rotacao_dupla_esquerda(NoAVL *no) {
    no->dir = avl_rotacao_direita(no->dir);
    return avl_rotacao_esquerda(no);
}