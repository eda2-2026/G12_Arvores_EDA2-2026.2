#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include "../back/paciente.h"
#include "../back/avl/avl.h"
#include "../back/leitor/leitor.h"

static Paciente criar_paciente_mock(int id, const char *cpf, const char *nome) {
    Paciente p;
    p.id_prontuario = id;
    strncpy(p.cpf, cpf, TAM_CPF - 1);
    p.cpf[TAM_CPF - 1] = '\0';
    strncpy(p.nome, nome, TAM_NOME - 1);
    p.nome[TAM_NOME - 1] = '\0';
    p.idade = 30;
    strcpy(p.sintomas, "Teste");
    strcpy(p.classificacao, "Verde");
    p.prioridade = 2;
    p.horario_chegada = 1000 + id;
    strcpy(p.status, "Aguardando");
    return p;
}

// verifica se todos os nos da arvore respeitam -1 <= FB <= 1
static int verificar_propriedade_avl(NoAVL *raiz) {
    if (!raiz) return 1;
    int fb = avl_fator_balanceamento(raiz);
    if (fb < -1 || fb > 1) return 0;
    return verificar_propriedade_avl(raiz->esq) && verificar_propriedade_avl(raiz->dir);
}

static void testar_rotacoes_e_balanceamento(void) {
    printf("[Teste 1] Validando rotacoes (LL, RR, LR, RL) e balanceamento...\n");

    Paciente p1 = criar_paciente_mock(1, "10000000000", "Paciente 10");
    Paciente p2 = criar_paciente_mock(2, "20000000000", "Paciente 20");
    Paciente p3 = criar_paciente_mock(3, "30000000000", "Paciente 30");
    Paciente p4 = criar_paciente_mock(4, "40000000000", "Paciente 40");
    Paciente p5 = criar_paciente_mock(5, "50000000000", "Paciente 50");
    Paciente p6 = criar_paciente_mock(6, "25000000000", "Paciente 25");

    NoAVL *raiz = NULL;

    //insercao crescente: 10, 20, 30 -> 20 sobe para a raiz
    raiz = avl_inserir(raiz, &p1);
    raiz = avl_inserir(raiz, &p2);
    raiz = avl_inserir(raiz, &p3);
    assert(strcmp(raiz->paciente->cpf, "20000000000") == 0);
    assert(avl_altura(raiz) == 2);

    //insere 50 e depois 40
    raiz = avl_inserir(raiz, &p5);
    raiz = avl_inserir(raiz, &p4);
    assert(verificar_propriedade_avl(raiz) == 1);

    //insere 25
    raiz = avl_inserir(raiz, &p6);
    assert(verificar_propriedade_avl(raiz) == 1);

    //testa bloqueio de CPF duplicado
    int altura_antes = avl_altura(raiz);
    raiz = avl_inserir(raiz, &p3);
    assert(avl_altura(raiz) == altura_antes);

    avl_liberar(raiz);

    // insercao decrescente: 30, 20, 10 -> 20 sobe para a raiz
    NoAVL *raiz_ll = NULL;
    raiz_ll = avl_inserir(raiz_ll, &p3);
    raiz_ll = avl_inserir(raiz_ll, &p2);
    raiz_ll = avl_inserir(raiz_ll, &p1);
    assert(strcmp(raiz_ll->paciente->cpf, "20000000000") == 0);
    assert(verificar_propriedade_avl(raiz_ll) == 1);
    avl_liberar(raiz_ll);

    printf("  -> OK! Todas as rotacoes mantiveram -1 <= FB <= 1.\n");
}

static void testar_busca_cpf(void) {
    printf("[Teste 2] Validando busca por CPF e contador de comparacoes...\n");

    Paciente p1 = criar_paciente_mock(1, "11111111111", "Ana");
    Paciente p2 = criar_paciente_mock(2, "22222222222", "Bruno");
    Paciente p3 = criar_paciente_mock(3, "33333333333", "Carlos");

    NoAVL *raiz = NULL;
    raiz = avl_inserir(raiz, &p1);
    raiz = avl_inserir(raiz, &p2);
    raiz = avl_inserir(raiz, &p3);

    int comp = 0;

    // Busca na raiz
    Paciente *achado = avl_buscar_cpf(raiz, "22222222222", &comp);
    assert(achado != NULL);
    assert(achado->id_prontuario == 2);
    assert(comp == 1);

    // Busca na folha esquerda
    achado = avl_buscar_cpf(raiz, "11111111111", &comp);
    assert(achado != NULL);
    assert(achado->id_prontuario == 1);
    assert(comp == 2);

    // Busca de CPF inexistente
    achado = avl_buscar_cpf(raiz, "99999999999", &comp);
    assert(achado == NULL);
    assert(comp == 2);

    avl_liberar(raiz);
    printf("  -> OK! Buscas existentes, de borda e inexistentes validadas.\n");
}

static void testar_carga_real_e_altura_maxima(void) {
    printf("[Teste 3] Validando carga real do CSV, altura maxima e memoria...\n");

    Paciente **pool = alocar_pool_pacientes(MAX_PACIENTES);
    assert(pool != NULL);

    int total = carregar_pacientes_csv("dados/pacientes.csv", pool, MAX_PACIENTES);
    if (total <= 0) {
        total = carregar_pacientes_csv("../dados/pacientes.csv", pool, MAX_PACIENTES);
    }
    assert(total > 0);

    NoAVL *raiz = NULL;
    for (int i = 0; i < total; i++) {
        raiz = avl_inserir(raiz, pool[i]);
    }

    int h = avl_altura(raiz);
    printf("  -> Pacientes inseridos: %d | Altura da AVL: %d\n", total, h);

    //limite teorico da AVL para ate 100.000 nos: h <= 24
    assert(h > 0 && h <= 24);
    assert(verificar_propriedade_avl(raiz) == 1);

    //busca nas extremidades e no meio garantindo que passos <= altura
    int indices[3] = {0, total / 2, total - 1};
    for (int i = 0; i < 3; i++) {
        int comp = 0;
        int idx = indices[i];
        Paciente *achado = avl_buscar_cpf(raiz, pool[idx]->cpf, &comp);
        assert(achado == pool[idx]);
        assert(comp >= 1 && comp <= h);
    }

    avl_liberar(raiz);
    liberar_pool_pacientes(pool, total);

    printf("  -> OK! Altura controlada e memoria liberada com sucesso.\n");
}

int main(void) {
    printf("=== INICIANDO TESTES UNITARIOS DA ARVORE AVL ===\n\n");

    testar_rotacoes_e_balanceamento();
    testar_busca_cpf();
    testar_carga_real_e_altura_maxima();

    printf("\n=== TODOS OS TESTES PASSARAM COM SUCESSO! ===\n");
    return 0;
}