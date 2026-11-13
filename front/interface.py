import sys
import os
import customtkinter as ctk
from tkinter import messagebox

diretorio_raiz = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if diretorio_raiz not in sys.path:
    sys.path.insert(0, diretorio_raiz)

from front.conexao_back import ConexaoBackend
from front.aba_consultorio import AbaConsultorio
from front.aba_prontuario import AbaProntuario
from front.aba_triagem import AbaTriagem

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AppTriagem(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Triagem Hospitalar SUS / Protocolo de Manchester - EDA2")
        self.geometry("1180x740")
        self.minsize(1000, 640)

        try:
            self.backend = ConexaoBackend()
        except Exception as e:
            messagebox.showerror(
                "Erro de Conexão com Backend",
                f"Falha ao iniciar o processo em C:\n\n{e}"
            )
            self.destroy()
            return

        self.protocol("WM_DELETE_WINDOW", self.on_fechar_janela)

        self._construir_cabecalho()
        self._construir_tabview()
        self.atualizar_barra_status()

    def _construir_cabecalho(self):
        self.frame_header = ctk.CTkFrame(self, fg_color="#181A1B", corner_radius=0, height=85)
        self.frame_header.pack(fill="x", padx=0, pady=(0, 5))
        self.frame_header.grid_columnconfigure(0, weight=1)
        self.frame_header.grid_columnconfigure(1, weight=0)

        frame_titulos = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        frame_titulos.grid(row=0, column=0, padx=20, pady=12, sticky="w")

        lbl_logo = ctk.CTkLabel(
            frame_titulos,
            text="UPA Central - Gestão de Emergência SUS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_logo.pack(anchor="w")

        lbl_subtitulo = ctk.CTkLabel(
            frame_titulos,
            text="EDA2 2026.2 | Protocolo de Manchester | Fila de Prioridades (Max-Heap) e Índice CPF (Árvore AVL)",
            font=ctk.CTkFont(size=12),
            text_color="#9E9E9E"
        )
        lbl_subtitulo.pack(anchor="w", pady=(2, 0))

        self.frame_metricas = ctk.CTkFrame(self.frame_header, fg_color="transparent")
        self.frame_metricas.grid(row=0, column=1, padx=20, pady=12, sticky="e")

        self.card_total = self._criar_card_metrica(self.frame_metricas, "PACIENTES TOTAIS", "...", "#263238")
        self.card_total.pack(side="left", padx=5)

        self.card_heap = self._criar_card_metrica(self.frame_metricas, "AGUARDANDO (HEAP)", "...", "#1B5E20")
        self.card_heap.pack(side="left", padx=5)

        self.card_avl = self._criar_card_metrica(self.frame_metricas, "ALTURA AVL (CPF)", "...", "#0D47A1")
        self.card_avl.pack(side="left", padx=5)

        self.card_status = self._criar_card_metrica(self.frame_metricas, "BACKEND", "CONECTADO", "#37474F")
        self.card_status.pack(side="left", padx=5)

    def _criar_card_metrica(self, master, titulo, valor_padrao, cor_fundo):
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

        card.lbl_val = lbl_val
        return card

    def _construir_tabview(self):
        self.tabview = ctk.CTkTabview(self, corner_radius=10)
        self.tabview.pack(fill="both", expand=True, padx=15, pady=(5, 15))

        tab_medico = self.tabview.add("Consultório Médico")
        self.aba_consultorio = AbaConsultorio(
            master_tab=tab_medico,
            backend=self.backend,
            callback_atualizar_status=self.atualizar_barra_status
        )

        tab_prontuario = self.tabview.add("Prontuário e Reclassificação")
        self.aba_prontuario = AbaProntuario(
            master_tab=tab_prontuario,
            backend=self.backend,
            callback_atualizar_sistema=self._sincronizar_abas
        )

        tab_triagem = self.tabview.add("Recepção e Triagem")
        self.aba_triagem = AbaTriagem(
            master_tab=tab_triagem,
            backend=self.backend,
            callback_atualizar_sistema=self._sincronizar_abas
        )

    def _sincronizar_abas(self):
        self.atualizar_barra_status()
        if hasattr(self, "aba_consultorio"):
            self.aba_consultorio.atualizar_radar()

    def atualizar_barra_status(self):
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
