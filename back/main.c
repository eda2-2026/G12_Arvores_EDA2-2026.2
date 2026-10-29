// teste de carga provisório
#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include "paciente.h"
#include "leitor.h"

int main() {
    printf("===================================================\n");
    printf("   TESTE DE CARGA DE PACIENTES - TRIAGEM HOSPITALAR\n");
    printf("===================================================\n\n");

    Paciente **pool = alocar_pool_pacientes(MAX_PACIENTES);
    if (!pool) {
        return 1;
    }

    const char *caminho_csv = "../dados/pacientes.csv";

    printf("Carregando base de dados: %s\n", caminho_csv);
    clock_t inicio = clock();

    int total = carregar_pacientes_csv(caminho_csv, pool, MAX_PACIENTES);

    clock_t fim = clock();
    double tempo_carga = (double)(fim - inicio) / CLOCKS_PER_SEC;

    if (total <= 0) {
        //caminho relativo alternativo caso execute da raiz
        total = carregar_pacientes_csv("dados/pacientes.csv", pool, MAX_PACIENTES);
    }

    if (total <= 0) {
        fprintf(stderr, "Erro ao carregar dados do arquivo CSV.\n");
        liberar_pool_pacientes(pool, 0);
        return 1;
    }

    printf("Carga concluida com sucesso!\n");
    printf("Total de pacientes carregados: %d\n", total);
    printf("Tempo total de leitura e alocacao: %.4f segundos\n\n", tempo_carga);

    //conferindo os 2 primeiros e o ultimo registro
    printf("--- Validacao de Integridade ---\n");
    printf("Primeiro: [ID: %d] %s | CPF: %s | Idade: %d | Gravidade: %s (P: %d) | Status: %s\n",
           pool[0]->id_prontuario, pool[0]->nome, pool[0]->cpf, pool[0]->idade,
           pool[0]->classificacao, pool[0]->prioridade, pool[0]->status);

    if (total > 1) {
        printf("Segundo:  [ID: %d] %s | CPF: %s | Idade: %d | Gravidade: %s (P: %d) | Status: %s\n",
               pool[1]->id_prontuario, pool[1]->nome, pool[1]->cpf, pool[1]->idade,
               pool[1]->classificacao, pool[1]->prioridade, pool[1]->status);
    }

    printf("Ultimo:   [ID: %d] %s | CPF: %s | Idade: %d | Gravidade: %s (P: %d) | Status: %s\n\n",
           pool[total - 1]->id_prontuario, pool[total - 1]->nome, pool[total - 1]->cpf, pool[total - 1]->idade,
           pool[total - 1]->classificacao, pool[total - 1]->prioridade, pool[total - 1]->status);

    liberar_pool_pacientes(pool, total);
    printf("Memoria liberada com sucesso.\n");
    return 0;
}