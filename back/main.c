#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "paciente.h"
#include "leitor/leitor.h"
#include "heap/heap.h"
#include "avl/avl.h"

#define TAM_BUFFER_CMD 1024

static void limpar_quebra_linha(char *str) {
    if (!str) return;
    size_t len = strlen(str);
    while (len > 0 && (str[len - 1] == '\n' || str[len - 1] == '\r')) {
        str[len - 1] = '\0';
        len--;
    }
}

int main(void) {
    
    setvbuf(stdout, NULL, _IONBF, 0);
    
    Paciente **pool = alocar_pool_pacientes(MAX_PACIENTES);
    if (!pool) {
        fprintf(stderr, "ERRO;Falha ao alocar pool de memoria para pacientes\n");
        return 1;
    }

    
    const char *caminho_csv = "dados/pacientes.csv";
    int total_carregados = carregar_pacientes_csv(caminho_csv, pool, MAX_PACIENTES);
    if (total_carregados <= 0) {
        caminho_csv = "../dados/pacientes.csv";
        total_carregados = carregar_pacientes_csv(caminho_csv, pool, MAX_PACIENTES);
    }

    if (total_carregados <= 0) {
        fprintf(stderr, "ERRO;Arquivo CSV de pacientes nao encontrado\n");
        liberar_pool_pacientes(pool, 0);
        return 1;
    }

    
    Heap *fila_heap = heap_criar(total_carregados + 2000);
    if (!fila_heap) {
        fprintf(stderr, "ERRO;Falha ao inicializar o Max-Heap\n");
        liberar_pool_pacientes(pool, total_carregados);
        return 1;
    }
    heap_construir_bottom_up(fila_heap, pool, total_carregados);

    
    NoAVL *raiz_avl = NULL;
    for (int i = 0; i < total_carregados; i++) {
        raiz_avl = avl_inserir(raiz_avl, pool[i]);
    }

    
    printf("PRONTO;%d;%d;Sistema de Triagem inicializado com sucesso\n", 
           total_carregados, avl_altura(raiz_avl));
    fflush(stdout);

    
    char buffer[TAM_BUFFER_CMD];

    while (fgets(buffer, sizeof(buffer), stdin) != NULL) {
        limpar_quebra_linha(buffer);
        if (strlen(buffer) == 0) continue;

        
        if (strcmp(buffer, "CHAMAR") == 0) {
            Paciente *chamado = heap_extrair_max(fila_heap);
            if (!chamado) {
                printf("ERRO;Fila de espera vazia\n");
            } else {
                printf("OK;%d;%s;%s;%d;%s;%s;%d;%lld;%s\n",
                       chamado->id_prontuario,
                       chamado->cpf,
                       chamado->nome,
                       chamado->idade,
                       chamado->sintomas,
                       chamado->classificacao,
                       chamado->prioridade,
                       chamado->horario_chegada,
                       chamado->status);
            }
            fflush(stdout);
        }
        
        else if (strncmp(buffer, "BUSCAR ", 7) == 0) {
            const char *cpf = buffer + 7;
            while (*cpf == ' ') cpf++; 

            int comparacoes = 0;
            Paciente *encontrado = avl_buscar_cpf(raiz_avl, cpf, &comparacoes);

            if (!encontrado) {
                printf("ERRO;Paciente com CPF %s nao encontrado\n", cpf);
            } else {
                printf("OK;%d;%d;%s;%s;%d;%s;%s;%d;%lld;%s\n",
                       comparacoes,
                       encontrado->id_prontuario,
                       encontrado->cpf,
                       encontrado->nome,
                       encontrado->idade,
                       encontrado->sintomas,
                       encontrado->classificacao,
                       encontrado->prioridade,
                       encontrado->horario_chegada,
                       encontrado->status);
            }
            fflush(stdout);
        }
        
        else if (strncmp(buffer, "RECLASSIFICAR ", 14) == 0) {
            int id = 0;
            int nova_prio = 0;
            char nova_cor[TAM_CLASSIFICACAO] = "";

            if (sscanf(buffer + 14, "%d %d %19s", &id, &nova_prio, nova_cor) == 3) {
                int res = heap_reclassificar(fila_heap, id, nova_prio, nova_cor);
                if (res) {
                    printf("OK;Paciente %d reclassificado para %s com prioridade %d\n", id, nova_cor, nova_prio);
                } else {
                    printf("ERRO;Paciente %d nao encontrado na fila de espera\n", id);
                }
            } else {
                printf("ERRO;Formato invalido. Use: RECLASSIFICAR <id> <prioridade> <classificacao>\n");
            }
            fflush(stdout);
        }
        
        else if (strncmp(buffer, "INSERIR ", 8) == 0) {
            char *dados = buffer + 8;
            char cpf[TAM_CPF] = "";
            char nome[TAM_NOME] = "";
            int idade = 0;
            char sintomas[TAM_SINTOMAS] = "";
            char classificacao[TAM_CLASSIFICACAO] = "";
            int prioridade = 0;

            
            char *token = strtok(dados, ";");
            if (token) strncpy(cpf, token, TAM_CPF - 1);

            token = strtok(NULL, ";");
            if (token) strncpy(nome, token, TAM_NOME - 1);

            token = strtok(NULL, ";");
            if (token) idade = atoi(token);

            token = strtok(NULL, ";");
            if (token) strncpy(sintomas, token, TAM_SINTOMAS - 1);

            token = strtok(NULL, ";");
            if (token) strncpy(classificacao, token, TAM_CLASSIFICACAO - 1);

            token = strtok(NULL, ";");
            if (token) prioridade = atoi(token);

            if (total_carregados < MAX_PACIENTES && strlen(cpf) > 0 && strlen(nome) > 0) {
                Paciente *novo = (Paciente*) malloc(sizeof(Paciente));
                if (novo) {
                    novo->id_prontuario = total_carregados + 1;
                    strncpy(novo->cpf, cpf, TAM_CPF - 1);
                    novo->cpf[TAM_CPF - 1] = '\0';
                    strncpy(novo->nome, nome, TAM_NOME - 1);
                    novo->nome[TAM_NOME - 1] = '\0';
                    novo->idade = idade;
                    strncpy(novo->sintomas, sintomas, TAM_SINTOMAS - 1);
                    novo->sintomas[TAM_SINTOMAS - 1] = '\0';
                    strncpy(novo->classificacao, classificacao, TAM_CLASSIFICACAO - 1);
                    novo->classificacao[TAM_CLASSIFICACAO - 1] = '\0';
                    novo->prioridade = prioridade;
                    novo->horario_chegada = (long long) time(NULL);
                    strncpy(novo->status, "Aguardando", TAM_STATUS - 1);
                    novo->status[TAM_STATUS - 1] = '\0';

                    
                    pool[total_carregados] = novo;
                    total_carregados++;

                    
                    heap_inserir(fila_heap, novo);
                    raiz_avl = avl_inserir(raiz_avl, novo);

                    printf("OK;%d;%d;Paciente inserido com sucesso na fila e no prontuario\n",
                           novo->id_prontuario, heap_tamanho(fila_heap));
                } else {
                    printf("ERRO;Falha de memoria ao alocar novo paciente\n");
                }
            } else {
                printf("ERRO;Dados invalidos ou capacidade maxima atingida\n");
            }
            fflush(stdout);
        }
        
        else if (strncmp(buffer, "FILA_TOPO", 9) == 0) {
            int n = 10;
            if (strlen(buffer) > 9) {
                n = atoi(buffer + 10);
            }
            if (n < 0) n = 0;
            if (n > heap_tamanho(fila_heap)) n = heap_tamanho(fila_heap);

            printf("FILA_INICIO;%d\n", n);
            for (int i = 0; i < n; i++) {
                Paciente *p = fila_heap->dados[i];
                printf("%d;%s;%s;%d;%s;%s;%d;%lld;%s\n",
                       p->id_prontuario,
                       p->cpf,
                       p->nome,
                       p->idade,
                       p->sintomas,
                       p->classificacao,
                       p->prioridade,
                       p->horario_chegada,
                       p->status);
            }
            printf("FILA_FIM\n");
            fflush(stdout);
        }
        
        else if (strcmp(buffer, "STATUS") == 0) {
            printf("OK;%d;%d;%d;%d\n",
                   total_carregados,
                   heap_tamanho(fila_heap),
                   avl_altura(raiz_avl),
                   fila_heap->capacidade);
            fflush(stdout);
        }
        
        else if (strcmp(buffer, "SAIR") == 0) {
            printf("OK;Encerrando backend\n");
            fflush(stdout);
            break;
        }
        else {
            printf("ERRO;Comando desconhecido: %s\n", buffer);
            fflush(stdout);
        }
    }

    
    avl_liberar(raiz_avl);
    heap_liberar(fila_heap);
    liberar_pool_pacientes(pool, total_carregados);

    return 0;
}