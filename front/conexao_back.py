import os
import subprocess
import threading
import time

class ConexaoBackend:
    def __init__(self):
        self.diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.diretorio_back = os.path.join(self.diretorio_raiz, "back")
        self.caminho_binario = os.path.join(self.diretorio_back, "main.out")
        
        self.processo = None
        self.lock = threading.Lock()
        
        self.total_carregados = 0
        self.altura_avl_inicial = 0
        
        self._compilar_se_necessario()
        self._iniciar_processo()

    def _compilar_se_necessario(self):
        if not os.path.exists(self.caminho_binario):
            print("[Backend] Executavel C nao encontrado. Compilando automaticamente...")
            comando = [
                "gcc", "-Wall", "-Wextra", "-pedantic", "-std=c11",
                "main.c", "leitor/leitor.c", "heap/heap.c", "avl/avl.c",
                "-o", "main.out"
            ]
            resultado = subprocess.run(
                comando,
                cwd=self.diretorio_back,
                capture_output=True,
                text=True
            )
            if resultado.returncode != 0:
                raise RuntimeError(f"Erro de compilacao no backend C:\n{resultado.stderr}")
            print("[Backend] Compilacao concluida com sucesso!")

    def _iniciar_processo(self):
        self.processo = subprocess.Popen(
            [self.caminho_binario],
            cwd=self.diretorio_raiz,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )

        linha_pronto = self.processo.stdout.readline().strip()
        if not linha_pronto.startswith("PRONTO;"):
            self.encerrar()
            raise RuntimeError(f"Falha ao iniciar backend C: {linha_pronto}")

        partes = linha_pronto.split(";")
        self.total_carregados = int(partes[1])
        self.altura_avl_inicial = int(partes[2])

    def _enviar_comando(self, comando):
        with self.lock:
            if not self.processo or self.processo.poll() is not None:
                raise RuntimeError("Processo do backend C nao esta em execucao.")

            self.processo.stdin.write(comando.strip() + "\n")
            self.processo.stdin.flush()

            linha_resposta = self.processo.stdout.readline().strip()
            return linha_resposta

    def _parsear_paciente(self, partes):
        # Converte a lista de campos em dicionario estruturado
        return {
            "id_prontuario": int(partes[0]),
            "cpf": partes[1],
            "nome": partes[2],
            "idade": int(partes[3]),
            "sintomas": partes[4],
            "classificacao": partes[5],
            "prioridade": int(partes[6]),
            "horario_chegada": int(partes[7]),
            "status": partes[8]
        }

    def chamar_proximo(self):
        resposta = self._enviar_comando("CHAMAR")
        partes = resposta.split(";")
        if partes[0] == "OK":
            return {
                "sucesso": True,
                "paciente": self._parsear_paciente(partes[1:])
            }
        return {"sucesso": False, "mensagem": partes[1] if len(partes) > 1 else resposta}

    def buscar_cpf(self, cpf):
        cpf_limpo = str(cpf).strip().replace(".", "").replace("-", "")
        resposta = self._enviar_comando(f"BUSCAR {cpf_limpo}")
        partes = resposta.split(";")
        if partes[0] == "OK":
            comparacoes = int(partes[1])
            paciente = self._parsear_paciente(partes[2:])
            return {
                "sucesso": True,
                "comparacoes": comparacoes,
                "paciente": paciente
            }
        return {"sucesso": False, "mensagem": partes[1] if len(partes) > 1 else resposta}

    def reclassificar(self, id_prontuario, nova_prioridade, nova_classificacao):
        comando = f"RECLASSIFICAR {id_prontuario} {nova_prioridade} {nova_classificacao}"
        resposta = self._enviar_comando(comando)
        partes = resposta.split(";")
        if partes[0] == "OK":
            return {"sucesso": True, "mensagem": partes[1]}
        return {"sucesso": False, "mensagem": partes[1] if len(partes) > 1 else resposta}

    def inserir_paciente(self, cpf, nome, idade, sintomas, classificacao, prioridade, horario_chegada=None):
        cpf_limpo = str(cpf).strip().replace(".", "").replace("-", "")
        if horario_chegada is None:
            horario_chegada = int(time.time())

        comando = f"INSERIR {cpf_limpo};{nome};{idade};{sintomas};{classificacao};{prioridade};{horario_chegada}"
        resposta = self._enviar_comando(comando)
        partes = resposta.split(";")
        if partes[0] == "OK":
            return {
                "sucesso": True,
                "id_prontuario": int(partes[1]),
                "mensagem": partes[2]
            }
        return {"sucesso": False, "mensagem": partes[1] if len(partes) > 1 else resposta}

    def obter_fila_topo(self, limite=10):
        with self.lock:
            if not self.processo or self.processo.poll() is not None:
                raise RuntimeError("Processo do backend C nao esta em execucao.")

            self.processo.stdin.write(f"FILA_TOPO {limite}\n")
            self.processo.stdin.flush()

            linha_inicio = self.processo.stdout.readline().strip()
            partes_inicio = linha_inicio.split(";")
            if partes_inicio[0] != "FILA_INICIO":
                return []

            qtd = int(partes_inicio[1])
            fila = []
            for _ in range(qtd):
                linha = self.processo.stdout.readline().strip()
                partes = linha.split(";")
                if len(partes) >= 9:
                    fila.append(self._parsear_paciente(partes))

            linha_fim = self.processo.stdout.readline().strip()
            assert linha_fim == "FILA_FIM", f"Esperado FILA_FIM, obtido: {linha_fim}"
            return fila

    def obter_status(self):
        resposta = self._enviar_comando("STATUS")
        partes = resposta.split(";")
        if partes[0] == "OK":
            return {
                "sucesso": True,
                "total_pacientes": int(partes[1]),
                "tamanho_heap": int(partes[2]),
                "altura_avl": int(partes[3]),
                "capacidade_maxima": int(partes[4])
            }
        return {"sucesso": False, "mensagem": partes[1] if len(partes) > 1 else resposta}

    def encerrar(self):
        with self.lock:
            if self.processo and self.processo.poll() is None:
                try:
                    self.processo.stdin.write("SAIR\n")
                    self.processo.stdin.flush()
                    self.processo.wait(timeout=3)
                except Exception:
                    self.processo.kill()
                finally:
                    self.processo = None