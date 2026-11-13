import customtkinter as ctk
from tkinter import messagebox
from front.tema_manchester import CORES_MANCHESTER, obter_estilo_manchester, formatar_cpf, formatar_timestamp


class AbaProntuario:
    def __init__(self, master_tab, backend, callback_atualizar_sistema=None):
        self.master = master_tab
        self.backend = backend
        self.callback_atualizar_sistema = callback_atualizar_sistema

        self.paciente_consultado = None
        self.comparacoes_ultima_busca = 0
        self.cor_selecionada = "Vermelho"
        self.prioridade_selecionada = 5

        self._construir_layout()

    def _construir_layout(self):
        self.master.grid_columnconfigure(0, weight=6, uniform="col_pront")
        self.master.grid_columnconfigure(1, weight=4, uniform="col_pront")
        self.master.grid_rowconfigure(0, weight=0)
        self.master.grid_rowconfigure(1, weight=1)

        # Barra de busca por CPF
        self.frame_busca = ctk.CTkFrame(self.master, corner_radius=10)
        self.frame_busca.grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 5), sticky="ew")
        self.frame_busca.grid_columnconfigure(1, weight=1)

        lbl_busca = ctk.CTkLabel(
            self.frame_busca,
            text="Consultar CPF (Árvore AVL):",
            font=ctk.CTkFont(size=15, weight="bold")
        )
        lbl_busca.grid(row=0, column=0, padx=(20, 10), pady=15, sticky="w")

        self.entry_cpf = ctk.CTkEntry(
            self.frame_busca,
            placeholder_text="000.000.000-00",
            font=ctk.CTkFont(size=15),
            height=40
        )
        self.entry_cpf.grid(row=0, column=1, padx=5, pady=15, sticky="ew")
        self.entry_cpf.bind("<KeyRelease>", self._aplicar_mascara_cpf)
        self.entry_cpf.bind("<Return>", self.on_buscar_cpf)

        self.btn_buscar = ctk.CTkButton(
            self.frame_busca,
            text="Buscar Prontuário",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=170,
            fg_color="#0D47A1",
            hover_color="#1565C0",
            command=self.on_buscar_cpf
        )
        self.btn_buscar.grid(row=0, column=2, padx=(5, 10), pady=15)

        self.lbl_metricas_avl = ctk.CTkLabel(
            self.frame_busca,
            text="AVL: Aguardando consulta",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="#263238",
            text_color="#80DEEA",
            corner_radius=6,
            width=210,
            height=40
        )
        self.lbl_metricas_avl.grid(row=0, column=3, padx=(5, 20), pady=15)

        self.col_ficha = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_ficha.grid(row=1, column=0, padx=(10, 5), pady=(5, 10), sticky="nsew")
        self.col_ficha.grid_columnconfigure(0, weight=1)
        self.col_ficha.grid_rowconfigure(1, weight=1)

        lbl_tit_ficha = ctk.CTkLabel(
            self.col_ficha,
            text="Ficha Médica do Paciente",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_tit_ficha.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        self.container_ficha = ctk.CTkFrame(self.col_ficha, corner_radius=8, fg_color="#1E1E1E")
        self.container_ficha.grid(row=1, column=0, padx=20, pady=(5, 20), sticky="nsew")
        self.container_ficha.grid_columnconfigure(0, weight=1)
        self.container_ficha.grid_rowconfigure(0, weight=1)

        self._renderizar_ficha_vazia()

        self.col_reclass = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_reclass.grid(row=1, column=1, padx=(5, 10), pady=(5, 10), sticky="nsew")
        self.col_reclass.grid_columnconfigure(0, weight=1)
        self._construir_painel_reclassificacao()

    def _aplicar_mascara_cpf(self, event=None):
        if event and event.keysym in ("BackSpace", "Delete", "Left", "Right", "Tab"):
            return

        digitos = "".join(filter(str.isdigit, self.entry_cpf.get()))[:11]
        if len(digitos) <= 3:
            formatado = digitos
        elif len(digitos) <= 6:
            formatado = f"{digitos[:3]}.{digitos[3:]}"
        elif len(digitos) <= 9:
            formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:]}"
        else:
            formatado = f"{digitos[:3]}.{digitos[3:6]}.{digitos[6:9]}-{digitos[9:]}"

        if self.entry_cpf.get() != formatado:
            self.entry_cpf.delete(0, "end")
            self.entry_cpf.insert(0, formatado)

    def _limpar_container_ficha(self):
        for widget in self.container_ficha.winfo_children():
            widget.destroy()

    def _renderizar_ficha_vazia(self):
        self._limpar_container_ficha()

        frame_vazio = ctk.CTkFrame(self.container_ficha, fg_color="transparent")
        frame_vazio.place(relx=0.5, rely=0.5, anchor="center")

        lbl_msg = ctk.CTkLabel(
            frame_vazio,
            text="Nenhum prontuário selecionado.",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#CFD8DC"
        )
        lbl_msg.pack()

        lbl_dica = ctk.CTkLabel(
            frame_vazio,
            text="Digite um CPF na barra acima (ex: 000.000.001-91) para buscar na Árvore AVL.",
            font=ctk.CTkFont(size=13),
            text_color="#78909C"
        )
        lbl_dica.pack(pady=(5, 0))

    def _renderizar_ficha_paciente(self, paciente, comparacoes):
        self._limpar_container_ficha()
        estilo = obter_estilo_manchester(paciente["classificacao"])

        card = ctk.CTkFrame(
            self.container_ficha,
            corner_radius=8,
            fg_color=estilo["fundo_suave"],
            border_color=estilo["borda"],
            border_width=2
        )
        card.pack(fill="both", expand=True, padx=15, pady=15)
        card.grid_columnconfigure(0, weight=1)

        frame_badge = ctk.CTkFrame(card, fg_color=estilo["fundo"], corner_radius=6, height=36)
        frame_badge.pack(fill="x", padx=15, pady=(15, 10))

        lbl_badge = ctk.CTkLabel(
            frame_badge,
            text=f"CLASSIFICAÇÃO ATUAL: {estilo['rotulo']}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=estilo["texto"]
        )
        lbl_badge.pack(pady=6)

        lbl_nome = ctk.CTkLabel(
            card,
            text=paciente["nome"],
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FFFFFF"
        )
        lbl_nome.pack(anchor="w", padx=20, pady=(5, 5))

        frame_info = ctk.CTkFrame(card, fg_color="transparent")
        frame_info.pack(fill="x", padx=20, pady=5)
        frame_info.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            frame_info,
            text=f"CPF: {formatar_cpf(paciente['cpf'])}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        ).grid(row=0, column=0, sticky="w", pady=3)

        ctk.CTkLabel(
            frame_info,
            text=f"Idade: {paciente['idade']} anos",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        ).grid(row=0, column=1, sticky="w", pady=3)

        ctk.CTkLabel(
            frame_info,
            text=f"Prontuário Nº: #{paciente['id_prontuario']}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        ).grid(row=1, column=0, sticky="w", pady=3)

        ctk.CTkLabel(
            frame_info,
            text=f"Chegada: {formatar_timestamp(paciente['horario_chegada'])}",
            font=ctk.CTkFont(size=14),
            text_color="#B0BEC5"
        ).grid(row=1, column=1, sticky="w", pady=3)

        ctk.CTkLabel(
            card,
            text="Sintomas / Quadro Clínico:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ECEFF1"
        ).pack(anchor="w", padx=20, pady=(12, 2))

        caixa_sintomas = ctk.CTkTextbox(
            card,
            height=68,
            corner_radius=6,
            fg_color="#121212",
            text_color="#ECEFF1",
            font=ctk.CTkFont(size=13)
        )
        caixa_sintomas.pack(fill="x", padx=20, pady=(2, 10))
        caixa_sintomas.insert("1.0", paciente["sintomas"])
        caixa_sintomas.configure(state="disabled")

        frame_rodape = ctk.CTkFrame(card, fg_color="transparent")
        frame_rodape.pack(fill="x", padx=20, pady=(5, 15))

        ctk.CTkLabel(
            frame_rodape,
            text=f"Status: {paciente['status'].upper()}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#FFD54F"
        ).pack(side="left")

        ctk.CTkLabel(
            frame_rodape,
            text=f"Busca AVL: {comparacoes} comparações O(log N)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#80DEEA"
        ).pack(side="right")

    def on_buscar_cpf(self, event=None):
        cpf_limpo = "".join(filter(str.isdigit, self.entry_cpf.get()))
        if len(cpf_limpo) != 11:
            messagebox.showwarning("CPF Inválido", "Digite um CPF completo com 11 dígitos numéricos.")
            return

        try:
            resposta = self.backend.buscar_cpf(cpf_limpo)
            if resposta["sucesso"]:
                self.paciente_consultado = resposta["paciente"]
                self.comparacoes_ultima_busca = resposta["comparacoes"]

                self.lbl_metricas_avl.configure(
                    text=f"AVL: {self.comparacoes_ultima_busca} comparações",
                    fg_color="#1B5E20",
                    text_color="#FFFFFF"
                )
                self._renderizar_ficha_paciente(self.paciente_consultado, self.comparacoes_ultima_busca)
            else:
                self.paciente_consultado = None
                self.lbl_metricas_avl.configure(
                    text="AVL: CPF não encontrado",
                    fg_color="#B71C1C",
                    text_color="#FFFFFF"
                )
                self._renderizar_ficha_vazia()
                messagebox.showinfo("Busca AVL", f"Nenhum paciente encontrado com o CPF {formatar_cpf(cpf_limpo)}.")
        except Exception as e:
            messagebox.showerror("Erro de Comunicação", f"Falha ao buscar CPF na AVL:\n{e}")

    def _construir_painel_reclassificacao(self):
        ctk.CTkLabel(
            self.col_reclass,
            text="Reclassificação Clínica",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(anchor="w", padx=20, pady=(15, 2))

        ctk.CTkLabel(
            self.col_reclass,
            text="Selecione o novo nível de risco (atualiza o Max-Heap):",
            font=ctk.CTkFont(size=12),
            text_color="#B0BEC5"
        ).pack(anchor="w", padx=20, pady=(0, 10))

        opcoes = [
            ("Vermelho", 5),
            ("Laranja", 4),
            ("Amarelo", 3),
            ("Verde", 2),
            ("Azul", 1)
        ]

        for cor, prio in opcoes:
            estilo = CORES_MANCHESTER[cor]
            btn = ctk.CTkButton(
                self.col_reclass,
                text=estilo["rotulo"],
                font=ctk.CTkFont(size=13, weight="bold"),
                height=38,
                fg_color=estilo["fundo"],
                text_color=estilo["texto"],
                hover_color=estilo["borda"],
                anchor="w",
                command=lambda c=cor, p=prio: self.selecionar_cor_manchester(c, p)
            )
            btn.pack(fill="x", padx=20, pady=4)

        self.lbl_selecao_atual = ctk.CTkLabel(
            self.col_reclass,
            text="Novo risco selecionado: Vermelho (Prioridade 5)",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#EF5350"
        )
        self.lbl_selecao_atual.pack(pady=(12, 8))

        self.btn_reclassificar = ctk.CTkButton(
            self.col_reclass,
            text="RECLASSIFICAR RISCO NO HEAP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            fg_color="#C62828",
            hover_color="#E53935",
            command=self.on_reclassificar_risco
        )
        self.btn_reclassificar.pack(fill="x", padx=20, pady=(5, 15))

    def selecionar_cor_manchester(self, cor, prioridade):
        self.cor_selecionada = cor
        self.prioridade_selecionada = prioridade
        estilo = CORES_MANCHESTER[cor]
        self.lbl_selecao_atual.configure(
            text=f"Novo risco selecionado: {cor} (Prioridade {prioridade})",
            text_color=estilo["borda"]
        )

    def on_reclassificar_risco(self):
        if not self.paciente_consultado:
            messagebox.showwarning("Aviso", "Busque um paciente pelo CPF antes de reclassificar.")
            return

        id_pront = self.paciente_consultado["id_prontuario"]
        cpf_atual = self.paciente_consultado["cpf"]

        try:
            res = self.backend.reclassificar(
                id_pront,
                self.prioridade_selecionada,
                self.cor_selecionada
            )
            if res["sucesso"]:
                # Consulta novamente na AVL para refletir a memoria compartilhada
                busca = self.backend.buscar_cpf(cpf_atual)
                if busca["sucesso"]:
                    self.paciente_consultado = busca["paciente"]
                    self._renderizar_ficha_paciente(self.paciente_consultado, busca["comparacoes"])

                if self.callback_atualizar_sistema:
                    self.callback_atualizar_sistema()

                messagebox.showinfo(
                    "Reclassificação Concluída",
                    f"Paciente #{id_pront} atualizado para {self.cor_selecionada} (Prioridade {self.prioridade_selecionada})!"
                )
            else:
                messagebox.showerror("Não Permitido", res.get("mensagem", "Falha ao reclassificar paciente."))
        except Exception as e:
            messagebox.showerror("Erro de Comunicação", f"Erro ao reclassificar no backend:\n{e}")
