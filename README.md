# G12_Arvores_EDA2-2026.2
# Sistema de Triagem e Gestão de Emergência Hospitalar (Protocolo de Manchester)

Trabalho prático 2 para a disciplina de Estruturas de Dados 2.

## 📹 Apresentação
* **Assista ao Vídeo:** [Apresentação da dupla](link_do_video_aqui) *(a ser gravado)*

## Equipe
*   [Gabriel Diniz](https://github.com/GabrielDiniz12) - 241025630
*   [Pedro Americo](https://github.com/dev-americo) - 241025980

## Descrição do Problema
O objetivo deste projeto é simular o fluxo de atendimento de urgência e emergência hospitalar baseado no **Protocolo de Classificação de Risco de Manchester**, processando uma base com **100.000 pacientes**.

O sistema atende a dois desafios fundamentais:
1. **Chamada prioritária imediata:** Garantir que pacientes em estado mais crítico (vermelho/laranja) sejam chamados primeiro, desempatando pelo tempo de chegada na unidade.
2. **Localização instantânea de prontuários:** Permitir que médicos e atendentes busquem a ficha clínica de qualquer paciente pelo **CPF**, além de possibilitar a **reclassificação de risco** em tempo real quando o quadro clínico se altera.

## Arquitetura da Solução
O sistema adota arquitetura desacoplada:
1. **Backend (C):** Responsável pela alocação em memória, manipulação do arquivo CSV e implementação das estruturas de dados de alta performance, operando via pipes de comunicação IPC (`stdin`/`stdout`).
2. **Frontend (Python / CustomTkinter):** Interface gráfica interativa moderna com suporte a tema escuro e visualização das filas por cores oficiais de Manchester.

## Estruturas de Dados e Algoritmos (C)
* **Fila de Prioridades (Max-Heap):** 
  * Gerencia a fila de espera dos atendimentos.
  * Prioridade definida pelo nível Manchester (1 a 5) com desempate por timestamp de chegada.
  * Suporte a inserção, extração do topo e reclassificação dinâmica de prioridade (`increase_key`) em tempo $O(\log N)$.
* **Árvore Binária Balanceada (AVL):** 
  * Indexa os prontuários dos pacientes utilizando o **CPF** como chave de busca.
  * Balanceamento automático por rotações (LL, RR, LR, RL), garantindo altura estritamente controlada e busca em tempo $O(\log N)$ com contador de comparações.

---

## 🚀 Como Executar o Projeto *(Em desenvolvimento)*

> [!NOTE]
> As instruções detalhadas de compilação do backend e execução da interface gráfica serão atualizadas conforme a conclusão dos módulos nas próximas issues.

### Pré-requisitos
* Compilador **GCC** (para o código C).
* **Python 3** com `customtkinter` (para a Interface Gráfica).

---

## Check-list de Desenvolvimento
- [ ] Configuração do repositório, diretórios e documentação base.
- [ ] Geração e higienização da base de dados (100.000 pacientes clínicos em CSV).
- [ ] `backend`: Definição da `struct Paciente` e leitor de CSV com pool de memória.
- [ ] `backend`: Implementação da Fila de Prioridades (Max-Heap).
- [ ] `backend`: Implementação da Árvore Binária Balanceada (AVL).
- [ ] `backend`: Bateria de Testes Unitários e validação com Valgrind.
- [ ] `backend`: Protocolo de comunicação IPC e `main.c`.
- [ ] `frontend`: Módulo de conexão Python-C (`subprocess`).
- [ ] `frontend`: Interface - Consultório Médico e Chamada de Pacientes.
- [ ] `frontend`: Interface - Prontuário, Busca por CPF e Reclassificação.
- [ ] `frontend`: Interface - Recepção e Nova Triagem.
- [ ] Gravação e entrega do vídeo de apresentação (5 min).