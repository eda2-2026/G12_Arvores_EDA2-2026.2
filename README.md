# Sistema de Triagem e Gestão de Emergência Hospitalar

Trabalho prático 3 para a disciplina de Estruturas de Dados e Algoritmos 2 (EDA2) — UnB/FGA.

## Apresentação
* **Assista ao Vídeo:** [Apresentação da dupla](link_do_video_aqui) *(a ser gravado na Issue #12)*

## Equipe
* [Gabriel Diniz](https://github.com/GabrielDiniz12) - 241025630
* [Pedro Americo](https://github.com/dev-americo) - 241025980

## Descrição do Problema
O objetivo deste projeto é simular o fluxo de atendimento de urgência e emergência hospitalar baseado no **Protocolo de Classificação de Risco de Manchester**, processando uma base real higienizada com **48.941 pacientes** (`dados/pacientes.csv`).

O sistema atende a dois desafios fundamentais:
1. **Chamada prioritária imediata:** Garantir que pacientes em estado mais crítico (Vermelho a Azul) sejam chamados primeiro, utilizando o horário de chegada como critério de desempate (FIFO na mesma gravidade).
2. **Localização instantânea de prontuários e reclassificação:** Permitir que médicos e atendentes busquem a ficha clínica de qualquer paciente pelo **CPF** em tempo logarítmico, além de possibilitar a **reclassificação de risco** em tempo real e o cadastro de novos atendimentos na recepção.

## Arquitetura da Solução
O sistema adota uma arquitetura desacoplada com **Zero-Copy em memória compartilhada**:
1. **Backend (C11):** Aloca os pacientes uma única vez em um *pool* de memória (`Paciente*`). Tanto o **Max-Heap** quanto a **Árvore AVL** armazenam apenas ponteiros para esses mesmos registros, mantendo os dados sincronizados instantaneamente. Opera como processo *daemon* via pipes IPC (`stdin`/`stdout`).
2. **Frontend (Python / CustomTkinter):** Interface gráfica em tema escuro organizada em três módulos integrados:
   * **Consultório Médico:** Chamada de pacientes por gravidade via Max-Heap e visualização da fila de espera.
   * **Prontuário e Reclassificação:** Busca por CPF via Árvore AVL (com contagem de comparações) e atualização dinâmica de risco.
   * **Recepção e Triagem:** Cadastro de novos pacientes com inserção simultânea na AVL e no Max-Heap.

## Estruturas de Dados e Algoritmos (C)
* **Fila de Prioridades (Max-Heap):**
  * Gerencia a fila de espera dos atendimentos em vetor contíguo (`Paciente **dados`).
  * Construção inicial Bottom-Up (Algoritmo de Floyd) em $O(N)$.
  * Prioridade definida pelo nível Manchester (5 a 1) com desempate pelo menor `horario_chegada`.
  * Suporte a inserção (`heap_inserir`), extração do topo (`heap_extrair_max`) e reclassificação dinâmica (`heap_reclassificar`) em tempo $O(\log N)$.
* **Árvore Binária Balanceada (AVL):**
  * Indexa os prontuários utilizando o **CPF** como chave de busca.
  * Balanceamento automático pelas 4 rotações clássicas (LL, RR, LR, RL), garantindo altura controlada (`16` para 48.941 registros) e busca em $O(\log N)$ com contador de comparações.

---

## Estrutura do Projeto

```text
G12_Arvores_EDA2-2026.2/
├── back/
│   ├── avl/            # Implementação da Árvore AVL (avl.c, avl.h)
│   ├── heap/           # Implementação do Max-Heap (heap.c, heap.h)
│   ├── leitor/         # Pool de memória e parser CSV (leitor.c, leitor.h)
│   ├── main.c          # Daemon IPC (stdin/stdout)
│   └── paciente.h      # Definição da struct Paciente
├── dados/
│   ├── pacientes.csv   # Base com 48.941 registros clínicos
│   └── setup_dados.py  # Script de geração/higienização
├── front/
│   ├── aba_consultorio.py
│   ├── aba_prontuario.py
│   ├── aba_triagem.py
│   ├── conexao_back.py # Ponte Python <-> C via subprocess
│   ├── interface.py    # Janela principal CustomTkinter
│   └── tema_manchester.py
└── test/
    ├── test_avl.c      # Testes unitários da Árvore AVL
    ├── test_heap.c     # Testes unitários do Max-Heap
    └── test_ipc.py     # Teste de integração Python <-> C
```

---

## Como Executar o Projeto

### Pré-requisitos
* Compilador **GCC** (suporte a `-std=c11`)
* **Python 3** com a biblioteca `customtkinter`:
  ```bash
  pip install customtkinter
  ```
* **Valgrind** *(opcional, para auditoria de memória)*

### 1. Executar a Interface Gráfica (Sistema Completo)
Na raiz do repositório, execute:
```bash
python3 front/interface.py
```
*(Caso o executável `back/main.out` ainda não exista, o módulo `conexao_back.py` compila o código C automaticamente antes de iniciar a interface).*

### 2. Compilar o Backend Manualmente (Opcional)
```bash
gcc -Wall -Wextra -pedantic -std=c11 back/main.c back/leitor/leitor.c back/heap/heap.c back/avl/avl.c -o back/main.out
```

### 3. Executar a Bateria de Testes e Valgrind
* **Testes Unitários do Max-Heap:**
  ```bash
  gcc -Wall -Wextra -pedantic -std=c11 test/test_heap.c back/heap/heap.c back/leitor/leitor.c -o test/test_heap.out && ./test/test_heap.out
  ```
* **Testes Unitários da Árvore AVL:**
  ```bash
  gcc -Wall -Wextra -pedantic -std=c11 test/test_avl.c back/avl/avl.c back/leitor/leitor.c -o test/test_avl.out && ./test/test_avl.out
  ```
* **Teste de Integração IPC (Python $\leftrightarrow$ C):**
  ```bash
  python3 test/test_ipc.py
  ```
* **Auditoria de Memória (Valgrind):**
  ```bash
  printf "STATUS\nSAIR\n" | valgrind --leak-check=full back/main.out
  ```

---

## Check-list de Desenvolvimento
- [X] Configuração do repositório, diretórios e documentação base.
- [X] Geração e higienização da base de dados (48.941 pacientes).
- [X] `backend`: Definição da `struct Paciente` e leitor de CSV com pool de memória.
- [X] `backend`: Implementação da Fila de Prioridades (Max-Heap).
- [X] `backend`: Implementação da Árvore Binária Balanceada (AVL).
- [X] `backend`: Bateria de Testes Unitários e validação com Valgrind (0 leaks).
- [X] `backend`: Protocolo de comunicação IPC e `main.c`.
- [X] `frontend`: Módulo de conexão Python-C (`subprocess`).
- [X] `frontend`: Interface — Consultório Médico e Chamada de Pacientes.
- [X] `frontend`: Interface — Prontuário, Busca por CPF e Reclassificação.
- [X] `frontend`: Interface — Recepção e Nova Triagem.
- [ ] Gravação e entrega do vídeo de apresentação (5 min — Issue #12).
