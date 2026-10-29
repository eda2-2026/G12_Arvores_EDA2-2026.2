#ifndef PACIENTE_H
#define PACIENTE_H

#define MAX_PACIENTES 100000
#define TAM_CPF 15
#define TAM_NOME 100
#define TAM_SINTOMAS 300
#define TAM_CLASSIFICACAO 20
#define TAM_STATUS 20

typedef struct {
    int id_prontuario;
    char cpf[TAM_CPF];
    char nome[TAM_NOME];
    int idade;
    char sintomas[TAM_SINTOMAS];
    char classificacao[TAM_CLASSIFICACAO];
    int prioridade;           //1 a 5 (Azul a Vermelho)
    long long horario_chegada; 
    char status[TAM_STATUS];  //"Aguardando", "Atendido"...
} Paciente;

#endif