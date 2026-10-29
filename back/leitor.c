#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "leitor.h"

#define TAM_LINHA_CSV 1024

Paciente** alocar_pool_pacientes(int capacidade) {
    Paciente **pool = (Paciente **)malloc(capacidade * sizeof(Paciente *));
    if (!pool) {
        fprintf(stderr, "Erro: Falha ao alocar pool de ponteiros de pacientes.\n");
        return NULL;
    }
    return pool;
}

void liberar_pool_pacientes(Paciente **pool, int total) {
    if (!pool) return;
    for (int i = 0; i < total; i++) {
        if (pool[i]) {
            free(pool[i]);
        }
    }
    free(pool);
}

int carregar_pacientes_csv(const char *caminho_csv, Paciente **pool, int capacidade_max) {
    FILE *f = fopen(caminho_csv, "r");
    if (!f) {
        fprintf(stderr, "Erro: Nao foi possivel abrir o arquivo '%s'.\n", caminho_csv);
        return -1;
    }

    char linha[TAM_LINHA_CSV];

    if (!fgets(linha, sizeof(linha), f)) {
        fclose(f);
        return 0;
    }

    int total_lidos = 0;

    while (fgets(linha, sizeof(linha), f) && total_lidos < capacidade_max) {
        //remove \r ou \n do final da linha
        linha[strcspn(linha, "\r\n")] = '\0';

        Paciente *p = (Paciente *)malloc(sizeof(Paciente));
        if (!p) {
            fprintf(stderr, "Erro de memoria ao alocar paciente na linha %d.\n", total_lidos + 2);
            break;
        }

        char *salva_ptr = NULL;

        char *campo = strtok_r(linha, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        p->id_prontuario = atoi(campo);

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        strncpy(p->cpf, campo, TAM_CPF - 1);
        p->cpf[TAM_CPF - 1] = '\0';

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        strncpy(p->nome, campo, TAM_NOME - 1);
        p->nome[TAM_NOME - 1] = '\0';

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        p->idade = atoi(campo);

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        strncpy(p->sintomas, campo, TAM_SINTOMAS - 1);
        p->sintomas[TAM_SINTOMAS - 1] = '\0';

        //classificacao (Manchester)
        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        strncpy(p->classificacao, campo, TAM_CLASSIFICACAO - 1);
        p->classificacao[TAM_CLASSIFICACAO - 1] = '\0';

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        p->prioridade = atoi(campo);

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        p->horario_chegada = atoll(campo);

        campo = strtok_r(NULL, ";", &salva_ptr);
        if (!campo) { free(p); continue; }
        strncpy(p->status, campo, TAM_STATUS - 1);
        p->status[TAM_STATUS - 1] = '\0';

        pool[total_lidos++] = p;
    }

    fclose(f);
    return total_lidos;
}