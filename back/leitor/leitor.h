#ifndef LEITOR_H
#define LEITOR_H

#include "paciente.h"

Paciente** alocar_pool_pacientes(int capacidade);

void liberar_pool_pacientes(Paciente **pool, int total);

//retorna o numero de pacientes carregados, ou -1 p/ erro
int carregar_pacientes_csv(const char *caminho_csv, Paciente **pool, int capacidade_max); 

#endif