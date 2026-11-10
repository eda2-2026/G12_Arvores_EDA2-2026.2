#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <assert.h>
#include <time.h>
#include "../back/paciente.h"
#include "../back/leitor/leitor.h"
#include "../back/heap/heap.h"

static void test_ordem_manchester() {
    printf("[TESTE 1] Insercao e Ordem de Manchester... ");

    Heap *h = heap_criar(10);
    assert(h != NULL);
    assert(heap_esta_vazio(h) == 1);

    Paciente p_azul = {1, "111", "Carlos", 20, "Sintomas leves", "Azul", 1, 1000, "Aguardando"};
    Paciente p_verde = {2, "222", "Bruna", 25, "Dor de garganta", "Verde", 2, 1000, "Aguardando"};
    Paciente p_amarelo = {3, "333", "Marcos", 30, "Febre e tosse", "Amarelo", 3, 1000, "Aguardando"};
    Paciente p_laranja = {4, "444", "Fernanda", 40, "Falta de ar aguda", "Laranja", 4, 1000, "Aguardando"};
    Paciente p_vermelho = {5, "555", "Roberto", 65, "Parada iminente", "Vermelho", 5, 1000, "Aguardando"};

    assert(heap_inserir(h, &p_azul) == 1);
    assert(heap_inserir(h, &p_verde) == 1);
    assert(heap_inserir(h, &p_laranja) == 1);
    assert(heap_inserir(h, &p_vermelho) == 1);
    assert(heap_inserir(h, &p_amarelo) == 1);

    assert(heap_tamanho(h) == 5);
    assert(heap_verificar_propriedade(h) == 1);

    Paciente *chamado1 = heap_extrair_max(h);
    assert(chamado1->prioridade == 5);
    assert(strcmp(chamado1->status, "Em Atendimento") == 0);

    Paciente *chamado2 = heap_extrair_max(h);
    assert(chamado2->prioridade == 4);

    Paciente *chamado3 = heap_extrair_max(h);
    assert(chamado3->prioridade == 3);

    Paciente *chamado4 = heap_extrair_max(h);
    assert(chamado4->prioridade == 2);

    Paciente *chamado5 = heap_extrair_max(h);
    assert(chamado5->prioridade == 1);

    assert(heap_esta_vazio(h) == 1);
    assert(heap_extrair_max(h) == NULL);

    heap_liberar(h);
    printf("PASSOU!\n");
}

static void test_desempate_timestamp() {
    printf("[TESTE 2] Criterio de Desempate por Horario (FIFO em mesma prioridade)... ");

    Heap *h = heap_criar(5);

    Paciente p_cedo = {10, "001", "Chegou Cedo", 30, "Febre", "Amarelo", 3, 1500000000, "Aguardando"};
    Paciente p_medio = {11, "002", "Chegou Medio", 35, "Febre", "Amarelo", 3, 1500000500, "Aguardando"};
    Paciente p_tarde = {12, "003", "Chegou Tarde", 40, "Febre", "Amarelo", 3, 1500001000, "Aguardando"};

    heap_inserir(h, &p_tarde);
    heap_inserir(h, &p_cedo);
    heap_inserir(h, &p_medio);

    assert(heap_verificar_propriedade(h) == 1);

    Paciente *c1 = heap_extrair_max(h);
    assert(c1->id_prontuario == 10);

    Paciente *c2 = heap_extrair_max(h);
    assert(c2->id_prontuario == 11);

    Paciente *c3 = heap_extrair_max(h);
    assert(c3->id_prontuario == 12);

    heap_liberar(h);
    printf("PASSOU!\n");
}

static void test_reclassificacao_dinamica() {
    printf("[TESTE 3] Reclassificacao Dinamica de Risco... ");

    Heap *h = heap_criar(10);

    Paciente p1 = {101, "001", "Paciente Grave", 50, "Infarto", "Vermelho", 5, 2000, "Aguardando"};
    Paciente p2 = {102, "002", "Paciente Moderado", 45, "Falta ar", "Laranja", 4, 1500, "Aguardando"};
    Paciente p3 = {103, "003", "Paciente Leve", 25, "Gripe", "Verde", 2, 1000, "Aguardando"};

    heap_inserir(h, &p1);
    heap_inserir(h, &p2);
    heap_inserir(h, &p3);

    assert(heap_consultar_topo(h)->id_prontuario == 101);

    int ok = heap_reclassificar(h, 103, 5, "Vermelho");
    assert(ok == 1);
    assert(heap_verificar_propriedade(h) == 1);

    assert(heap_consultar_topo(h)->id_prontuario == 103);

    Paciente *chamado = heap_extrair_max(h);
    assert(chamado->id_prontuario == 103);
    assert(strcmp(chamado->classificacao, "Vermelho") == 0);

    ok = heap_reclassificar(h, 101, 1, "Azul");
    assert(ok == 1);
    assert(heap_verificar_propriedade(h) == 1);

    assert(heap_consultar_topo(h)->id_prontuario == 102);

    heap_liberar(h);
    printf("PASSOU!\n");
}

static void test_carga_bottom_up_csv() {
    printf("[TESTE 4] Carga de 48.941 Pacientes Reais com Floyd Bottom-Up O(N)...\n");

    Paciente **pool = alocar_pool_pacientes(MAX_PACIENTES);
    assert(pool != NULL);

    const char *caminho = "dados/pacientes.csv";
    int total = carregar_pacientes_csv(caminho, pool, MAX_PACIENTES);
    if (total <= 0) {
        total = carregar_pacientes_csv("../dados/pacientes.csv", pool, MAX_PACIENTES);
    }
    assert(total > 40000);
    printf("    -> %d pacientes carregados do CSV para o pool de memoria.\n", total);

    Heap *h = heap_criar(total);
    assert(h != NULL);

    clock_t t0 = clock();
    heap_construir_bottom_up(h, pool, total);
    clock_t t1 = clock();

    double tempo_bottom_up = (double)(t1 - t0) / CLOCKS_PER_SEC;
    printf("    -> Tempo de construcao Bottom-Up do Heap: %.4f segundos!\n", tempo_bottom_up);
    assert(heap_tamanho(h) == total);

    printf("    -> Validando propriedade do Max-Heap em todos os %d nos... ", total);
    int propriedade_valida = heap_verificar_propriedade(h);
    assert(propriedade_valida == 1);
    printf("VALIDADA COM SUCESSO!\n");

    printf("    -> Extraindo amostra de 10.000 pacientes verificando monotonicidade... ");
    Paciente *anterior = heap_extrair_max(h);
    assert(anterior != NULL);

    for (int i = 1; i < 10000; i++) {
        Paciente *atual = heap_extrair_max(h);
        assert(atual != NULL);

        assert(anterior->prioridade >= atual->prioridade);

        if (anterior->prioridade == atual->prioridade) {
            assert(anterior->horario_chegada <= atual->horario_chegada);
        }

        anterior = atual;
    }
    printf("PASSOU!\n");

    heap_liberar(h);
    liberar_pool_pacientes(pool, total);
}

int main() {
    printf("=====================================================\n");
    printf("   SUITE DE TESTES UNITARIOS: MAX-HEAP (ISSUE #4)   \n");
    printf("=====================================================\n\n");

    test_ordem_manchester();
    test_desempate_timestamp();
    test_reclassificacao_dinamica();
    test_carga_bottom_up_csv();

    printf("\n>>> TODOS OS TESTES PASSARAM COM 100%% DE SUCESSO! <<<\n");
    return 0;
}
