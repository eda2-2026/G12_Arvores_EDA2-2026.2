import customtkinter as ctk
from tkinter import messagebox
from front.tema_manchester import obter_estilo_manchester, formatar_cpf, formatar_timestamp

class AbaConsultorio:
    """
    Componente visual da Aba 1: Consultorio Medico e Chamada de Pacientes.
    Consome o Max-Heap em C em tempo real para gerenciar o atendimento da emergencia.
    """

    def __init__(self, master_tab, backend, callback_atualizar_status=None):
        self.master = master_tab
        self.backend = backend
        self.callback_atualizar_status = callback_atualizar_status

        self.paciente_atual = None

        self._construir_layout()
        self.atualizar_radar()

    def _construir_layout(self):
        # Configura grid da aba em 2 colunas proporcionais
        self.master.grid_columnconfigure(0, weight=6, uniform="col")
        self.master.grid_columnconfigure(1, weight=4, uniform="col")
        self.master.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # COLUNA ESQUERDA: Consultorio Medico & Chamada Ativa
        # -------------------------------------------------------------
        self.col_esquerda = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_esquerda.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.col_esquerda.grid_columnconfigure(0, weight=1)
        self.col_esquerda.grid_rowconfigure(1, weight=1)

        # Titulo da secao
        lbl_titulo_medico = ctk.CTkLabel(
            self.col_esquerda,
            text="🩺 Consultório de Atendimento Médico",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_titulo_medico.grid(row=0, column=0, padx=20, pady=(15, 10), sticky="w")

        # Container do Card Central de Atendimento
        self.container_card = ctk.CTkFrame(self.col_esquerda, corner_radius=8, fg_color="#1E1E1E")
        self.container_card.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.container_card.grid_columnconfigure(0, weight=1)
        self.container_card.grid_rowconfigure(0, weight=1)

        # Renderiza inicialmente o estado de espera
        self._renderizar_card_vazio()

        # Botoes de Acao no rodape da coluna esquerda
        frame_acoes = ctk.CTkFrame(self.col_esquerda, fg_color="transparent")
        frame_acoes.grid(row=2, column=0, padx=20, pady=(10, 20), sticky="ew")
        frame_acoes.grid_columnconfigure(0, weight=3)
        frame_acoes.grid_columnconfigure(1, weight=1)

        self.btn_chamar = ctk.CTkButton(
            frame_acoes,
            text="📢 CHAMAR PRÓXIMO PACIENTE (HEAP)",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=48,
            fg_color="#1B5E20",
            hover_color="#2E7D32",
            command=self.on_chamar_proximo
        )
        self.btn_chamar.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_finalizar = ctk.CTkButton(
            frame_acoes,
            text="✅ Concluir",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=48,
            fg_color="#37474F",
            hover_color="#455A64",
            command=self.on_concluir_atendimento
        )
        self.btn_finalizar.grid(row=0, column=1, sticky="ew")

        # -------------------------------------------------------------
        # COLUNA DIREITA: Radar de Espera (Top 10 do Max-Heap)
        # -------------------------------------------------------------
        self.col_direita = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_direita.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.col_direita.grid_columnconfigure(0, weight=1)
        self.col_direita.grid_rowconfigure(1, weight=1)

        # Cabecalho do Radar com botao de atualizacao manual
        frame_cabecalho_radar = ctk.CTkFrame(self.col_direita, fg_color="transparent")
        frame_cabecalho_radar.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")
        frame_cabecalho_radar.grid_columnconfigure(0, weight=1)

        lbl_titulo_radar = ctk.CTkLabel(
            frame_cabecalho_radar,
            text="⏱️ Radar da Fila de Espera",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_titulo_radar.grid(row=0, column=0, sticky="w")

        btn_atualizar_radar = ctk.CTkButton(
            frame_cabecalho_radar,
            text="🔄 Atualizar",
            width=90,
            height=30,
            font=ctk.CTkFont(size=12),
            fg_color="#37474F",
            hover_color="#455A64",
            command=self.atualizar_radar
        )
        btn_atualizar_radar.grid(row=0, column=1, sticky="e")

        lbl_subtitulo_radar = ctk.CTkLabel(
            self.col_direita,
            text="Top 10 pacientes de maior prioridade no Max-Heap:",
            font=ctk.CTkFont(size=12),
            text_color="#B0BEC5"
        )
        lbl_subtitulo_radar.grid(row=1, column=0, padx=15, pady=(0, 10), sticky="nw")

        # Scrollable Frame listando os proximos pacientes
        self.scroll_radar = ctk.CTkScrollableFrame(self.col_direita, corner_radius=8, fg_color="#1E1E1E")
        self.scroll_radar.grid(row=1, column=0, padx=15, pady=(28, 15), sticky="nsew")
        self.scroll_radar.grid_columnconfigure(0, weight=1)

    # -------------------------------------------------------------
    # Renderizacao do Card Central de Atendimento
    # -------------------------------------------------------------
    def _limpar_container_card(self):
        for widget in self.container_card.winfo_children():
            widget.destroy()

    def _renderizar_card_vazio(self):
        self._limpar_container_card()

        frame_vazio = ctk.CTkFrame(self.container_card, fg_color="transparent")
        frame_vazio.place(relx=0.5, rely=0.5, anchor="center")

        lbl_icone = ctk.CTkLabel(frame_vazio, text="👨‍⚕️", font=ctk.CTkFont(size=54))
        lbl_icone.pack(pady=(0, 10))

        lbl_msg = ctk.CTkLabel(
            frame_vazio,
            text="Nenhum paciente em atendimento no momento.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#CFD8DC"
        )
        lbl_msg.pack()

        lbl_dica = ctk.CTkLabel(
            frame_vazio,
            text="Clique no botão verde abaixo para chamar o próximo caso mais grave da fila.",
            font=ctk.CTkFont(size=13),
            text_color="#78909C"
        )
        lbl_dica.pack(pady=(5, 0))

    def _renderizar_card_paciente(self, paciente):
        self._limpar_container_card()
        estilo = obter_estilo_manchester(paciente["classificacao"])

        card = ctk.CTkFrame(
            self.container_card,
            corner_radius=8,
            fg_color=estilo["fundo_suave"],
            border_color=estilo["borda"],
            border_width=2
        )
        card.pack(fill="both", expand=True, padx=15, pady=15)
        card.grid_columnconfigure(0, weight=1)

        # 1. Badge Luminosa de Manchester
        frame_badge = ctk.CTkFrame(card, fg_color=estilo["fundo"], corner_radius=6, height=36)
        frame_badge.pack(fill="x", padx=15, pady=(15, 10))

        lbl_badge = ctk.CTkLabel(
            frame_badge,
            text=f"PROTOCOLO DE MANCHESTER: {estilo['rotulo']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=estilo["texto"]
        )
        lbl_badge.pack(pady=6)

        # 2. Nome e Dados Pessoais
        lbl_nome = ctk.CTkLabel(
            card,
            text=paciente["nome"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_nome.pack(anchor="w", padx=20, pady=(5, 5))

        # Grade com dados cadastrais
        frame_info = ctk.CTkFrame(card, fg_color="transparent")
        frame_info.pack(fill="x", padx=20, pady=5)
        frame_info.grid_columnconfigure((0, 1), weight=1)

        lbl_cpf = ctk.CTkLabel(
            frame_info,
            text=f"CPF: {formatar_cpf(paciente['cpf'])}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        )
        lbl_cpf.grid(row=0, column=0, sticky="w", pady=2)

        lbl_idade = ctk.CTkLabel(
            frame_info,
            text=f"Idade: {paciente['idade']} anos",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        )
        lbl_idade.grid(row=0, column=1, sticky="w", pady=2)

        lbl_prontuario = ctk.CTkLabel(
            frame_info,
            text=f"Prontuário Nº: #{paciente['id_prontuario']}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        )
        lbl_prontuario.grid(row=1, column=0, sticky="w", pady=2)

        lbl_chegada = ctk.CTkLabel(
            frame_info,
            text=f"Entrada: {formatar_timestamp(paciente['horario_chegada'])}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        )
        lbl_chegada.grid(row=1, column=1, sticky="w", pady=2)

        # 3. Queixa Clinica / Sintomas
        lbl_titulo_sintomas = ctk.CTkLabel(
            card,
            text="Queixa Clínica / Sintomas Relatados:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ECEFF1"
        )
        lbl_titulo_sintomas.pack(anchor="w", padx=20, pady=(15, 2))

        caixa_sintomas = ctk.CTkTextbox(
            card,
            height=70,
            corner_radius=6,
            fg_color="#121212",
            text_color="#ECEFF1",
            font=ctk.CTkFont(size=13)
        )
        caixa_sintomas.pack(fill="x", padx=20, pady=(2, 10))
        caixa_sintomas.insert("1.0", paciente["sintomas"])
        caixa_sintomas.configure(state="disabled")

        # 4. Status atual
        lbl_status = ctk.CTkLabel(
            card,
            text=f"Status: 🟡 {paciente['status'].upper()}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFD54F"
        )
        lbl_status.pack(anchor="w", padx=20, pady=(0, 15))

    # -------------------------------------------------------------
    # Renderizacao do Radar da Fila (Max-Heap)
    # -------------------------------------------------------------
    def atualizar_radar(self):
        for widget in self.scroll_radar.winfo_children():
            widget.destroy()

        try:
            proximos = self.backend.obter_fila_topo(limite=10)
        except Exception as e:
            lbl_erro = ctk.CTkLabel(
                self.scroll_radar,
                text=f"Erro ao consultar fila: {e}",
                text_color="#E53935"
            )
            lbl_erro.pack(pady=10)
            return

        if not proximos:
            lbl_vazio = ctk.CTkLabel(
                self.scroll_radar,
                text="Fila de espera vazia no momento!",
                text_color="#81C784"
            )
            lbl_vazio.pack(pady=20)
            return

        for idx, p in enumerate(proximos, start=1):
            estilo = obter_estilo_manchester(p["classificacao"])

            card_item = ctk.CTkFrame(
                self.scroll_radar,
                corner_radius=6,
                fg_color="#262626",
                border_color=estilo["borda"],
                border_width=1
            )
            card_item.pack(fill="x", padx=5, pady=4)
            card_item.grid_columnconfigure(1, weight=1)

            # Posicao numerica no Heap
            lbl_pos = ctk.CTkLabel(
                card_item,
                text=f"{idx}º",
                font=ctk.CTkFont(size=15, weight="bold"),
                width=35,
                text_color="#FFFFFF"
            )
            lbl_pos.grid(row=0, column=0, rowspan=2, padx=(8, 4), pady=5)

            # Nome e Idade
            lbl_nome_item = ctk.CTkLabel(
                card_item,
                text=f"{p['nome']} ({p['idade']}a)",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#FFFFFF"
            )
            lbl_nome_item.grid(row=0, column=1, sticky="w", padx=4, pady=(5, 0))

            # Resumo de sintomas
            sintomas_curto = p["sintomas"][:42] + ("..." if len(p["sintomas"]) > 42 else "")
            lbl_sint_item = ctk.CTkLabel(
                card_item,
                text=sintomas_curto,
                font=ctk.CTkFont(size=11),
                text_color="#9E9E9E"
            )
            lbl_sint_item.grid(row=1, column=1, sticky="w", padx=4, pady=(0, 5))

            # Tag de Manchester colorida a direita
            badge_item = ctk.CTkLabel(
                card_item,
                text=f" {p['classificacao'].upper()} (P{p['prioridade']}) ",
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=estilo["fundo"],
                text_color=estilo["texto"],
                corner_radius=4
            )
            badge_item.grid(row=0, column=2, rowspan=2, padx=(4, 10), pady=8, sticky="e")

    # -------------------------------------------------------------
    # Eventos de Acao do Medico
    # -------------------------------------------------------------
    def on_chamar_proximo(self):
        try:
            resposta = self.backend.chamar_proximo()
            if resposta["sucesso"]:
                self.paciente_atual = resposta["paciente"]
                self._renderizar_card_paciente(self.paciente_atual)
                self.atualizar_radar()

                if self.callback_atualizar_status:
                    self.callback_atualizar_status()
            else:
                messagebox.showinfo(
                    "Fila Vazia",
                    "Não há mais pacientes aguardando na fila de emergência (Heap vazio)."
                )
        except Exception as e:
            messagebox.showerror("Erro de Comunicação", f"Falha ao chamar paciente:\n{e}")

    def on_concluir_atendimento(self):
        if not self.paciente_atual:
            messagebox.showinfo("Aviso", "Nenhum paciente em atendimento para concluir.")
            return

        nome = self.paciente_atual["nome"]
        self.paciente_atual = None
        self._renderizar_card_vazio()

        if self.callback_atualizar_status:
            self.callback_atualizar_status()

        messagebox.showinfo("Atendimento Concluído", f"Atendimento do paciente {nome} concluído com sucesso!")
