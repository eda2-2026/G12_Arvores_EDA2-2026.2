import os
import sys
import subprocess

def testar_ipc():
    print("=====================================================")
    print("   TESTE DE INTEGRACAO IPC: PYTHON <-> C (MAIN.C)   ")
    print("=====================================================\n")

    # Localiza a raiz do projeto
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, ".."))
    binario = os.path.join(raiz_projeto, "back", "main.out")

    # 1. Compilação do binário se não existir
    print("[1/8] Verificando e compilando binario do backend C...")
    cmd_compilar = [
        "gcc", "-Wall", "-Wextra",
        "back/main.c", "back/leitor/leitor.c", "back/heap/heap.c", "back/avl/avl.c",
        "-o", "back/main.out"
    ]
    res_comp = subprocess.run(cmd_compilar, cwd=raiz_projeto, capture_output=True, text=True)
    if res_comp.returncode != 0:
        print("FALHA NA COMPILACAO DO BACKEND:")
        print(res_comp.stderr)
        sys.exit(1)
    print("      -> Backend compilado com 0 erros!\n")

    # 2. Inicialização do Daemon
    print("[2/8] Inicializando processo daemon via subprocess.Popen...")
    proc = subprocess.Popen(
        [binario],
        cwd=raiz_projeto,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    # Lê mensagem de prontidão
    linha_pronto = proc.stdout.readline().strip()
    print(f"      -> Mensagem recebida: {linha_pronto}")
    assert linha_pronto.startswith("PRONTO;"), "Esperado cabecalho PRONTO"
    partes_pronto = linha_pronto.split(";")
    total_pacientes = int(partes_pronto[1])
    altura_avl = int(partes_pronto[2])
    print(f"      -> Total carregado: {total_pacientes} | Altura AVL: {altura_avl}\n")

    # 3. Teste do comando STATUS
    print("[3/8] Testando comando STATUS...")
    proc.stdin.write("STATUS\n")
    proc.stdin.flush()
    linha_status = proc.stdout.readline().strip()
    print(f"      -> Resposta: {linha_status}")
    assert linha_status.startswith("OK;"), "Esperado retorno OK no STATUS"
    print("      -> STATUS validado com sucesso!\n")

    # 4. Teste do comando FILA_TOPO 5 (Radar da Fila)
    print("[4/8] Testando comando FILA_TOPO 5...")
    proc.stdin.write("FILA_TOPO 5\n")
    proc.stdin.flush()
    linha_inicio = proc.stdout.readline().strip()
    assert linha_inicio == "FILA_INICIO;5", f"Esperado FILA_INICIO;5, obtido {linha_inicio}"
    
    pacientes_radar = []
    for _ in range(5):
        pacientes_radar.append(proc.stdout.readline().strip())
    
    linha_fim = proc.stdout.readline().strip()
    assert linha_fim == "FILA_FIM", f"Esperado FILA_FIM, obtido {linha_fim}"
    print(f"      -> Topo da fila recebido com {len(pacientes_radar)} pacientes:")
    for i, p in enumerate(pacientes_radar, 1):
        dados = p.split(";")
        print(f"         {i}. [ID {dados[0]}] {dados[2]} - {dados[5]} (Prio {dados[6]})")
    print("      -> FILA_TOPO validado com sucesso!\n")

    # 5. Teste do comando BUSCAR <cpf> (Consulta AVL)
    print("[5/8] Testando comando BUSCAR CPF na AVL...")
    cpf_teste = "00000000191"
    proc.stdin.write(f"BUSCAR {cpf_teste}\n")
    proc.stdin.flush()
    linha_busca = proc.stdout.readline().strip()
    print(f"      -> Resposta: {linha_busca}")
    assert linha_busca.startswith("OK;"), "Esperado OK na busca por CPF existente"
    partes_busca = linha_busca.split(";")
    comparacoes = int(partes_busca[1])
    nome = partes_busca[4]
    classificacao = partes_busca[7]
    print(f"      -> Paciente: {nome} | Gravidade: {classificacao} | Passos AVL: {comparacoes}")
    assert comparacoes <= 24, "Numero de comparacoes na AVL nao deve exceder 24"
    print("      -> BUSCAR validado com sucesso!\n")

    # 6. Teste do comando CHAMAR (Extração Max-Heap)
    print("[6/8] Testando comando CHAMAR (Heap Extract)...")
    proc.stdin.write("CHAMAR\n")
    proc.stdin.flush()
    linha_chamado = proc.stdout.readline().strip()
    print(f"      -> Chamado: {linha_chamado}")
    assert linha_chamado.startswith("OK;"), "Esperado OK na chamada"
    partes_chamado = linha_chamado.split(";")
    assert partes_chamado[6] == "Vermelho" or int(partes_chamado[7]) == 5, "Chamado deve ser de maxima gravidade (Vermelho)"
    assert partes_chamado[9] == "Em Atendimento", "Status deve mudar para Em Atendimento"
    print("      -> CHAMAR validado com sucesso!\n")

    # 7. Teste do comando RECLASSIFICAR
    print("[7/8] Testando comando RECLASSIFICAR...")
    proc.stdin.write("RECLASSIFICAR 1 5 Vermelho\n")
    proc.stdin.flush()
    linha_reclass = proc.stdout.readline().strip()
    print(f"      -> Resposta: {linha_reclass}")
    assert linha_reclass.startswith("OK;"), "Esperado OK na reclassificacao"

    # Confere se a AVL ja reflete a nova gravidade no mesmo instante (memoria compartilhada)
    proc.stdin.write(f"BUSCAR {cpf_teste}\n")
    proc.stdin.flush()
    linha_busca_pos = proc.stdout.readline().strip()
    partes_pos = linha_busca_pos.split(";")
    print(f"      -> Consulta pos-reclassificacao: Gravidade = {partes_pos[7]}, Prioridade = {partes_pos[8]}")
    assert partes_pos[7] == "Vermelho", "Paciente deve refletir classificacao Vermelho"
    assert partes_pos[8] == "5", "Paciente deve refletir prioridade 5"
    print("      -> Sincronizacao de memoria compartilhada validada com sucesso!\n")

    # 8. Teste do comando SAIR e Encerramento Limpo
    print("[8/8] Testando encerramento com comando SAIR...")
    proc.stdin.write("SAIR\n")
    proc.stdin.flush()
    linha_sair = proc.stdout.readline().strip()
    print(f"      -> Resposta: {linha_sair}")
    assert linha_sair == "OK;Encerrando backend", "Esperado encerramento limpo"
    proc.wait(timeout=5)
    assert proc.returncode == 0, f"Processo encerrou com codigo {proc.returncode}"
    print("      -> Processo C encerrado com codigo 0 (Sucesso)!\n")

    print(">>> TODOS OS TESTES DE INTEGRACAO IPC PASSARAM COM SUCESSO! <<<\n")

if __name__ == "__main__":
    testar_ipc()
