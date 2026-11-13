# Sistema de Triagem e Gestão de Emergência Hospitalar

Trabalho prático 3 para a disciplina de Estruturas de Dados 2.

## Apresentação
* **Assista ao Vídeo:** [![Assista à demonstração](https://img.youtube.com/vi/JB-06nm0UH4/maxresdefault.jpg)](https://www.youtube.com/watch?v=JB-06nm0UH4)

## Equipe
*   [Gabriel Diniz](https://github.com/GabrielDiniz12) - 241025630
*   [Pedro Americo](https://github.com/dev-americo) - 241025980

## Descrição do Problema
O objetivo deste projeto é simular o fluxo de atendimento de urgência e emergência hospitalar baseado no **Protocolo de Classificação de Risco de Manchester**, processando uma base com **50.000 pacientes**.

O sistema atende a dois desafios fundamentais:
1. **Chamada prioritária imediata:** Garantir que pacientes em estado mais crítico (vermelho/laranja) sejam chamados primeiro, desempatando pelo tempo de chegada na unidade.
2. **Localização instantânea de prontuários:** Permitir que médicos e atendentes busquem a ficha clínica de qualquer paciente pelo **CPF**, além de possibilitar a **reclassificação de risco** em tempo real quando o quadro clínico se altera.

## Arquitetura da Solução
O sistema adota arquitetura desacoplada:
1. **Backend (C):** Responsável pela alocação em memória, manipulação do arquivo CSV e implementação das estruturas de dados de alta performance, operando via pipes de comunicação IPC (`stdin`/`stdout`).
2. **Frontend (Python / CustomTkinter):** Interface gráfica interativa moderna com suporte a tema escuro e visualização das filas por cores oficiais de Manchester.

### Estrutura do Projeto

```text
G12_Arvores_EDA2-2026.2/
├── back/
│   ├── avl/            # Implementação da Árvore AVL (avl.c, avl.h)
│   ├── heap/           # Implementação do Max-Heap (heap.c, heap.h)
│   ├── leitor/         # Pool de memória e parser CSV (leitor.c, leitor.h)
│   ├── main.c          
│   └── paciente.h      # Definição da struct Paciente
├── dados/
│   ├── pacientes.csv   # Base com registros
│   └── setup_dados.py  # Script de geração
├── front/
│   ├── aba_consultorio.py
│   ├── aba_prontuario.py
│   ├── aba_triagem.py
│   ├── conexao_back.py
│   ├── interface.py    # Janela principal
│   └── tema_manchester.py
└── test/
    ├── test_avl.c      
    ├── test_heap.c     
    └── test_ipc.py     
```

---

## Como Executar o Projeto

### Pré-requisitos

- Compilador **GCC** (para o código C).
- **Python 3** com `customtkinter` (para a Interface Gráfica).
- Compilador **GCC** (suporte a `-std=c11`)
- **Python 3** com a biblioteca `customtkinter`:
  ```bash
  pip install customtkinter
  ```
- **Valgrind** *(opcional, para auditoria de memória)*

### 1. Executar a Interface Gráfica

Na raiz do repositório, execute:
```bash
python3 front/interface.py
```
*(Caso o executável `back/main.out` ainda não exista, o módulo `conexao_back.py` compila o código C automaticamente antes de iniciar a interface).*

### 2. Compilar o Backend Manualmente

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
