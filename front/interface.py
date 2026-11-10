import sys
import os
import customtkinter as ctk
from tkinter import messagebox

# Garante resolucao de imports quando executado diretamente
diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

from front.conexao_back import ConexaoBackend
from front.aba_consultorio import AbaConsultorio

# Configuracao global de aparencia do CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppTriagem(ctk.CTk):
    """
    Janela Principal da Aplicacao Desktop do Sistema de Triagem Hospitalar SUS / Manchester.
    
    Integra as estruturas de dados fundamentais em C (Max-Heap e Arvore AVL)
    a uma interface gráfica moderna e responsiva dividida em 3 abas operacionais.
    """

    def __init__(self):
        super().__init__()

        # Configuracoes da Janela Principal
        self.title("Sistema de Triagem Hospitalar SUS / Protocolo de Manchester — EDA2")
        self.geometry("1180x740")
        self.minsize(1000, 640)

        # Inicializacao da comunicacao IPC com o daemon C
        try:
            self.backend = ConexaoBackend()
        except Exception as e:
            messagebox.showerror(
                "Erro de Conexão com Backend",
                f"Falha crítica ao iniciar o daemon em C:\n\n{e}"
            )
            self.destroy()
            return

        # Protocolo de fechamento seguro (limpa subprocesso C)
        self.protocol("WM_DELETE_WINDOW", self.on_fechar_janela)

        # Construcao da Interface
        self._construir_cabecalho()
        self._construir_tabview()
        self.atualizar_barra_status()

    def _construir_cabecalho(self):
        """Barra de status e metricas no topo da aplicacao."""
        self.frame_header = ctk.CTkFrame(self, fg_color="#181A1B", corner_radius=0, height=85)
        self.frame_header.pack(fill="x", padx=0, pady=(0, 5))
        self.frame_header.grid_columnconfigure(0, weight=1)
        self.frame_header.grid_columnconfigure(1, weight=0)

        # Identificacao da UPA / Sistema
        frame_titulos = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        frame_titulos.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        lbl_logo = ctk.CTkLabel(
            frame_titulos,
            text="🏥 UPA Central — Gestão de Emergência SUS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_logo.pack(anchor="w")

        lbl_subtitulo = ctk.CTkLabel(
            frame_titulos,
            text="EDA2 2026.2 • Protocolo de Manchester • Fila de Prioridades (Max-Heap) & Índice CPF (Árvore AVL)",
            font=ctk.CTkFont(size=12),
            text_color="#9E9E9E"
        )
        lbl_subtitulo.pack(anchor="w", pady=(2, 0))

        # Indicadores de Metricas das Estruturas de Dados
        self.frame_metricas = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        self.frame_metricas.grid(row=0, column=1, padx=20, pady=12, sticky="e")

        # Card: Total Cadastrados
        self.card_total = self._criar_card_metrica(self.frame_metricas, "PACIENTES TOTAIS", "...", "#263238")
        self.card_total.pack(side="left", padx=5)

        # Card: Fila no Max-Heap
        self.card_heap = self._criar_card_metrica(self.frame_metricas, "AGUARDANDO (HEAP)", "...", "#1B5E20")
        self.card_heap.pack(side="left", padx=5)

        # Card: Altura da Arvore AVL
        self.card_avl = self._criar_card_metrica(self.frame_metricas, "ALTURA AVL (CPF)", "...", "#0D47A1")
        self.card_avl.pack(side="left", padx=5)

        # Card: Status Daemon IPC
        self.card_status = self._criar_card_metrica(self.frame_metricas, "BACKEND DAEMON", "CONECTADO", "#37474F")
        self.card_status.pack(side="left", padx=5)

    def _criar_card_metrica(self, master, titulo, valor_padrao, cor_fundo):
        """Cria um pequeno widget retangular para exibicao de indicador."""
        card = ctk.CTkFrame(master, fg_color=cor_fundo, corner_radius=6, width=130, height=52)
        card.pack_propagate(False)

        lbl_tit = ctk.CTkLabel(
            card,
            text=titulo,
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color="#B0BEC5"
        )
        lbl_tit.pack(pady=(4, 0))

        lbl_val = ctk.CTkLabel(
            card,
            text=valor_padrao,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_val.pack()

        # Guarda referencia interna do label de valor para atualizacoes dinamicas
        card.lbl_val = lbl_val
        return card

    def _construir_tabview(self):
        """Constroi o navegador com as 3 abas operacionais do sistema."""
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        # Aba 1: Consultorio Medico (Issue #9)
        tab_medico = self.tabview.add("🩺 Consultório Médico")
        self.aba_consultorio = AbaConsultorio(
            master_tab=tab_medico,
            backend=self.backend,
            callback_atualizar_status=self.atualizar_barra_status
        )

        # Aba 2: Prontuario e Reclassificacao (Issue #10 - Gabriel)
        tab_prontuario = self.tabview.add("🔍 Prontuário e Reclassificação")
        self._construir_placeholder_aba2(tab_prontuario)

        # Aba 3: Recepcao e Triagem (Issue #11 - Pedro)
        tab_triagem = self.tabview.add("📋 Recepção e Triagem")
        self._construir_placeholder_aba3(tab_triagem)

    def _construir_placeholder_aba2(self, master):
        """Placeholder informativo para a Issue #10 (Gabriel Diniz)."""
        frame = ctk.CTkFrame(master, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_icone = ctk.CTkLabel(frame, text="🔍", font=ctk.CTkFont(size=56))
        lbl_icone.pack(pady=(50, 10))

        lbl_tit = ctk.CTkLabel(
            frame,
            text="Módulo 8.2 — Prontuário, Busca e Reclassificação Dinâmica",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_tit.pack(pady=5)

        lbl_sub = ctk.CTkLabel(
            frame,
            text="Responsável: Gabriel Diniz (241025630) • Issue #10",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#29B6F6"
        )
        lbl_sub.pack(pady=5)

        desc = (
            "Este módulo realizará a busca binária de pacientes indexados por CPF via Árvore AVL em tempo O(log N),\n"
            "apresentando o histórico completo do paciente, tempo de espera e comparador de nós percorridos.\n"
            "Permitirá também a reclassificação de risco de Manchester, disparando a percolação (subir/descer) no Max-Heap."
        )
        lbl_desc = ctk.CTkLabel(
            frame,
            text=desc,
            font=ctk.CTkFont(size=13),
            text_color="#B0BEC5",
            justify="center"
        )
        lbl_desc.pack(pady=15)

    def _construir_placeholder_aba3(self, master):
        """Placeholder informativo para a Issue #11 (Pedro Américo)."""
        frame = ctk.CTkFrame(master, corner_radius=10)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        lbl_icone = ctk.CTkLabel(frame, text="📋", font=ctk.CTkFont(size=56))
        lbl_icone.pack(pady=(50, 10))

        lbl_tit = ctk.CTkLabel(
            frame,
            text="Módulo 8.3 — Recepção e Nova Triagem de Paciente",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_tit.pack(pady=5)

        lbl_sub = ctk.CTkLabel(
            frame,
            text="Responsável: Pedro Américo (241025980) • Issue #11",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#66BB6A"
        )
        lbl_sub.pack(pady=5)

        desc = (
            "Este módulo permitirá a recepção de novos pacientes que chegam à UPA em tempo real,\n"
            "com preenchimento de CPF, sintomas vitais e seleção assistida da cor de Manchester.\n"
            "A submissão inserirá simultaneamente o paciente na Árvore AVL de busca e no Max-Heap de prioridades."
        )
        lbl_desc = ctk.CTkLabel(
            frame,
            text=desc,
            font=ctk.CTkFont(size=13),
            text_color="#B0BEC5",
            justify="center"
        )
        lbl_desc.pack(pady=15)

    def atualizar_barra_status(self):
        """Consulta o backend C e atualiza as metricas da barra de topo."""
        try:
            status = self.backend.obter_status()
            if status.get("sucesso"):
                total = f"{status['total_pacientes']:,}".replace(",", ".")
                heap_tam = f"{status['tamanho_heap']:,}".replace(",", ".")
                altura = str(status["altura_avl"])

                self.card_total.lbl_val.configure(text=total)
                self.card_heap.lbl_val.configure(text=heap_tam)
                self.card_avl.lbl_val.configure(text=altura)
                self.card_status.lbl_val.configure(text="ATIVO", text_color="#66BB6A")
        except Exception:
            self.card_status.lbl_val.configure(text="ERRO", text_color="#EF5350")

    def on_fechar_janela(self):
        """Encerra graciosamente o processo C antes de fechar a interface Tkinter."""
        try:
            if hasattr(self, "backend") and self.backend:
                self.backend.encerrar()
        finally:
            self.destroy()


def main():
    app = AppTriagem()
    app.mainloop()


if __name__ == "__main__":
    main()
