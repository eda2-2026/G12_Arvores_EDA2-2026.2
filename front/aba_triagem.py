import time
import customtkinter as ctk
from tkinter import messagebox
from front.tema_manchester import (
    CORES_MANCHESTER,
    obter_estilo_manchester,
    formatar_cpf,
    formatar_timestamp
)


class AbaTriagem:
    """
    Componente visual da Aba 3: Recepção e Nova Triagem de Pacientes.
    
    Permite o cadastro de novos atendimentos na emergência hospitalar em tempo real,
    realizando a inserção simultânea e balanceada na Árvore AVL (indexação por CPF)
    e no Max-Heap (gerenciamento dinâmico da fila prioritária de Manchester) em O(log N).
    """

    def __init__(self, master_tab, backend, callback_atualizar_sistema=None):
        self.master = master_tab
        self.backend = backend
        self.callback_atualizar_sistema = callback_atualizar_sistema

        self.cor_selecionada = "Amarelo"
        self.prioridade_selecionada = 3
        self.botoes_manchester = {}

        self.paciente_recem_inserido = None
        self.historico_sessao = []

        self._construir_layout()

    def _construir_layout(self):
        # Grid com 2 colunas proporcionais (60% formulário, 40% confirmação/histórico)
        self.master.grid_columnconfigure(0, weight=6, uniform="col_triagem")
        self.master.grid_columnconfigure(1, weight=4, uniform="col_triagem")
        self.master.grid_rowconfigure(0, weight=1)

        # -------------------------------------------------------------
        # COLUNA ESQUERDA: Formulário de Triagem Clínica
        # -------------------------------------------------------------
        self.col_form = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_form.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="nsew")
        self.col_form.grid_columnconfigure(0, weight=1)

        # Cabeçalho da coluna esquerda
        lbl_tit_form = ctk.CTkLabel(
            self.col_form,
            text="Recepção e Nova Triagem Clínica",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        lbl_tit_form.grid(row=0, column=0, padx=20, pady=(15, 2), sticky="w")

        lbl_sub_form = ctk.CTkLabel(
            self.col_form,
            text="Inserção simultânea e balanceada no Max-Heap e na Árvore AVL em tempo O(log N)",
            font=ctk.CTkFont(size=12),
            text_color="#9E9E9E"
        )
        lbl_sub_form.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="w")

        # Container dos campos
        self.container_campos = ctk.CTkFrame(self.col_form, fg_color="#1E1E1E", corner_radius=8)
        self.container_campos.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        self.container_campos.grid_columnconfigure(0, weight=1)
        self.container_campos.grid_columnconfigure(1, weight=1)

        # 1. Nome Completo
        lbl_nome = ctk.CTkLabel(
            self.container_campos,
            text="Nome Completo do Paciente *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_nome.grid(row=0, column=0, columnspan=2, padx=15, pady=(12, 2), sticky="w")

        self.entry_nome = ctk.CTkEntry(
            self.container_campos,
            placeholder_text="Ex: Carlos Eduardo de Oliveira",
            font=ctk.CTkFont(size=14),
            height=36
        )
        self.entry_nome.grid(row=1, column=0, columnspan=2, padx=15, pady=(0, 10), sticky="ew")

        # 2. CPF e Idade lado a lado
        lbl_cpf = ctk.CTkLabel(
            self.container_campos,
            text="CPF (11 dígitos) *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_cpf.grid(row=2, column=0, padx=15, pady=(2, 2), sticky="w")

        lbl_idade = ctk.CTkLabel(
            self.container_campos,
            text="Idade (anos) *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_idade.grid(row=2, column=1, padx=15, pady=(2, 2), sticky="w")

        self.entry_cpf = ctk.CTkEntry(
            self.container_campos,
            placeholder_text="000.000.000-00",
            font=ctk.CTkFont(size=14),
            height=36
        )
        self.entry_cpf.grid(row=3, column=0, padx=(15, 10), pady=(0, 10), sticky="ew")
        self.entry_cpf.bind("<KeyRelease>", self._aplicar_mascara_cpf)

        self.entry_idade = ctk.CTkEntry(
            self.container_campos,
            placeholder_text="Ex: 42",
            font=ctk.CTkFont(size=14),
            height=36
        )
        self.entry_idade.grid(row=3, column=1, padx=(10, 15), pady=(0, 10), sticky="ew")

        # 3. Queixa Principal e Sintomas
        lbl_sintomas = ctk.CTkLabel(
            self.container_campos,
            text="Queixa Principal / Sintomas Apresentados *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_sintomas.grid(row=4, column=0, columnspan=2, padx=15, pady=(2, 2), sticky="w")

        self.entry_sintomas = ctk.CTkEntry(
            self.container_campos,
            placeholder_text="Ex: Falta de ar aguda, dor torácica, saturação 92%",
            font=ctk.CTkFont(size=14),
            height=36
        )
        self.entry_sintomas.grid(row=5, column=0, columnspan=2, padx=15, pady=(0, 12), sticky="ew")

        # 4. Classificação de Risco (Protocolo de Manchester)
        lbl_manchester = ctk.CTkLabel(
            self.container_campos,
            text="Classificação de Risco de Manchester (Prioridade de Atendimento) *",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        lbl_manchester.grid(row=6, column=0, columnspan=2, padx=15, pady=(4, 6), sticky="w")

        self._construir_botoes_manchester(self.container_campos, start_row=7)

        # Botoes de Acao no rodape da coluna esquerda
        frame_acoes = ctk.CTkFrame(self.col_form, fg_color="transparent")
        frame_acoes.grid(row=3, column=0, padx=20, pady=(10, 15), sticky="ew")
        frame_acoes.grid_columnconfigure(0, weight=3)
        frame_acoes.grid_columnconfigure(1, weight=1)

        self.btn_cadastrar = ctk.CTkButton(
            frame_acoes,
            text="CADASTRAR PACIENTE (ENVIAR À FILA)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46,
            fg_color="#1B5E20",
            hover_color="#2E7D32",
            command=self.on_cadastrar_paciente
        )
        self.btn_cadastrar.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.btn_limpar = ctk.CTkButton(
            frame_acoes,
            text="Limpar Campos",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=46,
            fg_color="#37474F",
            hover_color="#455A64",
            command=self._limpar_formulario
        )
        self.btn_limpar.grid(row=0, column=1, sticky="ew")

        # -------------------------------------------------------------
        # COLUNA DIREITA: Confirmação & Histórico Recente da Sessão
        # -------------------------------------------------------------
        self.col_direita = ctk.CTkFrame(self.master, corner_radius=10)
        self.col_direita.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.col_direita.grid_columnconfigure(0, weight=1)
        self.col_direita.grid_rowconfigure(1, weight=0)
        self.col_direita.grid_rowconfigure(3, weight=1)

        # Topo direito: Resumo da última triagem realizada
        lbl_tit_confirmacao = ctk.CTkLabel(
            self.col_direita,
            text="Confirmação da Última Triagem",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        lbl_tit_confirmacao.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        self.container_confirmacao = ctk.CTkFrame(self.col_direita, fg_color="#1E1E1E", corner_radius=8)
        self.container_confirmacao.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        self.container_confirmacao.grid_columnconfigure(0, weight=1)

        self._renderizar_confirmacao_vazia()

        # Base direita: Histórico da sessão
        self.lbl_tit_historico = ctk.CTkLabel(
            self.col_direita,
            text="Triagens Desta Sessão (0)",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.lbl_tit_historico.grid(row=2, column=0, padx=15, pady=(15, 5), sticky="w")

        self.scroll_historico = ctk.CTkScrollableFrame(self.col_direita, corner_radius=8)
        self.scroll_historico.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.scroll_historico.grid_columnconfigure(0, weight=1)

        self._renderizar_historico_vazio()

    def _construir_botoes_manchester(self, master, start_row):
        """Cria os 5 seletores visuais do Protocolo de Manchester."""
        frame_cores = ctk.CTkFrame(master, fg_color="transparent")
        frame_cores.grid(row=start_row, column=0, columnspan=2, padx=15, pady=(0, 12), sticky="ew")

        # Configura 5 colunas uniformes
        for i in range(5):
            frame_cores.grid_columnconfigure(i, weight=1, uniform="manchester_btn")

        opcoes = [
            ("Vermelho", 5, "Emergência (5)"),
            ("Laranja", 4, "Muito Urg. (4)"),
            ("Amarelo", 3, "Urgente (3)"),
            ("Verde", 2, "Pouco Urg. (2)"),
            ("Azul", 1, "Não Urg. (1)"),
        ]

        for idx, (cor, prio, rotulo) in enumerate(opcoes):
            estilo = CORES_MANCHESTER[cor]
            btn = ctk.CTkButton(
                frame_cores,
                text=rotulo,
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color=estilo["fundo"],
                text_color=estilo["texto"],
                height=34,
                border_width=3 if cor == self.cor_selecionada else 0,
                border_color="#FFFFFF" if cor == self.cor_selecionada else estilo["fundo"],
                command=lambda c=cor, p=prio: self._selecionar_manchester(c, p)
            )
            btn.grid(row=0, column=idx, padx=2, sticky="ew")
            self.botoes_manchester[cor] = btn

    def _selecionar_manchester(self, cor: str, prioridade: int):
        """Atualiza a classificacao selecionada e o destaque visual dos botoes."""
        self.cor_selecionada = cor
        self.prioridade_selecionada = prioridade

        for nome_cor, btn in self.botoes_manchester.items():
            if nome_cor == cor:
                btn.configure(border_width=3, border_color="#FFFFFF")
            else:
                btn.configure(border_width=0, border_color=CORES_MANCHESTER[nome_cor]["fundo"])

    def _aplicar_mascara_cpf(self, event=None):
        """Aplica formatacao automatica no campo de CPF."""
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

        self.entry_cpf.delete(0, "end")
        self.entry_cpf.insert(0, formatado)

    def _limpar_formulario(self):
        """Limpa todos os campos de entrada do formulario."""
        self.entry_nome.delete(0, "end")
        self.entry_cpf.delete(0, "end")
        self.entry_idade.delete(0, "end")
        self.entry_sintomas.delete(0, "end")
        self._selecionar_manchester("Amarelo", 3)

    def _renderizar_confirmacao_vazia(self):
        """Renderiza mensagem padrao quando nenhuma triagem foi realizada ainda."""
        for widget in self.container_confirmacao.winfo_children():
            widget.destroy()

        lbl_vazio = ctk.CTkLabel(
            self.container_confirmacao,
            text="Nenhum paciente cadastrado nesta sessão.\nPreencha o formulário ao lado para realizar uma triagem.",
            font=ctk.CTkFont(size=12),
            text_color="#78909C",
            justify="center"
        )
        lbl_vazio.pack(padx=20, pady=35)

    def _renderizar_confirmacao_sucesso(self):
        """Exibe o card completo do paciente recém-cadastrado no sistema."""
        for widget in self.container_confirmacao.winfo_children():
            widget.destroy()

        p = self.paciente_recem_inserido
        if not p:
            self._renderizar_confirmacao_vazia()
            return

        estilo = obter_estilo_manchester(p["classificacao"])

        # Badge de gravidade no topo
        badge = ctk.CTkLabel(
            self.container_confirmacao,
            text=f"CLASSIFICAÇÃO: {p['classificacao'].upper()} (PRIORIDADE {p['prioridade']})",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color=estilo["fundo"],
            text_color=estilo["texto"],
            corner_radius=6,
            height=28
        )
        badge.pack(padx=15, pady=(12, 8), fill="x")

        # Dados principais do paciente
        lbl_nome = ctk.CTkLabel(
            self.container_confirmacao,
            text=p["nome"],
            font=ctk.CTkFont(size=16, weight="bold")
        )
        lbl_nome.pack(padx=15, pady=(0, 2), anchor="w")

        info_linha = f"Prontuário #{p['id_prontuario']}  •  CPF: {formatar_cpf(p['cpf'])}  •  Idade: {p['idade']} anos"
        lbl_info = ctk.CTkLabel(
            self.container_confirmacao,
            text=info_linha,
            font=ctk.CTkFont(size=12),
            text_color="#B0BEC5"
        )
        lbl_info.pack(padx=15, pady=(0, 8), anchor="w")

        # Queixa clínica
        lbl_sintomas = ctk.CTkLabel(
            self.container_confirmacao,
            text=f"Sintomas: {p['sintomas']}",
            font=ctk.CTkFont(size=12),
            text_color="#ECEFF1",
            wraplength=380,
            justify="left"
        )
        lbl_sintomas.pack(padx=15, pady=(0, 10), anchor="w")

        # Caixa com status das Estruturas de Dados
        frame_status_ed = ctk.CTkFrame(self.container_confirmacao, fg_color="#263238", corner_radius=6)
        frame_status_ed.pack(padx=15, pady=(0, 12), fill="x")

        fila_heap_txt = f"Max-Heap: Posição estimada na fila (~{p.get('tamanho_heap', 'Atualizado')})"
        lbl_heap = ctk.CTkLabel(
            frame_status_ed,
            text=fila_heap_txt,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#81C784"
        )
        lbl_heap.pack(padx=10, pady=(6, 2), anchor="w")

        lbl_avl = ctk.CTkLabel(
            frame_status_ed,
            text="Árvore AVL: Prontuário indexado por CPF em tempo O(log N)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#80DEEA"
        )
        lbl_avl.pack(padx=10, pady=(2, 6), anchor="w")

    def _renderizar_historico_vazio(self):
        """Mensagem quando a lista de historico recente estiver vazia."""
        for widget in self.scroll_historico.winfo_children():
            widget.destroy()

        lbl_vazio = ctk.CTkLabel(
            self.scroll_historico,
            text="Aguardando cadastros...",
            font=ctk.CTkFont(size=12),
            text_color="#546E7A"
        )
        lbl_vazio.pack(pady=40)

    def _atualizar_historico_sessao(self):
        """Atualiza a lista de pacientes cadastrados durante a sessao."""
        for widget in self.scroll_historico.winfo_children():
            widget.destroy()

        self.lbl_tit_historico.configure(text=f"Triagens Desta Sessão ({len(self.historico_sessao)})")

        if not self.historico_sessao:
            self._renderizar_historico_vazio()
            return

        for p in self.historico_sessao:
            estilo = obter_estilo_manchester(p["classificacao"])
            card_item = ctk.CTkFrame(self.scroll_historico, fg_color="#1E1E1E", corner_radius=6)
            card_item.pack(fill="x", padx=5, pady=3)
            card_item.grid_columnconfigure(1, weight=1)

            # Badge colorido lateral
            badge = ctk.CTkLabel(
                card_item,
                text=f" {p['prioridade']} ",
                font=ctk.CTkFont(size=12, weight="bold"),
                fg_color=estilo["fundo"],
                text_color=estilo["texto"],
                corner_radius=4,
                width=24,
                height=24
            )
            badge.grid(row=0, column=0, rowspan=2, padx=(8, 10), pady=6)

            # Nome e dados
            lbl_n = ctk.CTkLabel(
                card_item,
                text=p["nome"],
                font=ctk.CTkFont(size=13, weight="bold")
            )
            lbl_n.grid(row=0, column=1, sticky="w", pady=(6, 0))

            sub_txt = f"#{p['id_prontuario']} • {p['classificacao']} • {formatar_cpf(p['cpf'])}"
            lbl_s = ctk.CTkLabel(
                card_item,
                text=sub_txt,
                font=ctk.CTkFont(size=11),
                text_color="#90A4AE"
            )
            lbl_s.grid(row=1, column=1, sticky="w", pady=(0, 6))

    def on_cadastrar_paciente(self):
        """Valida os campos do formulário e insere o paciente no sistema via IPC."""
        nome = self.entry_nome.get().strip()
        cpf_raw = self.entry_cpf.get().strip()
        idade_str = self.entry_idade.get().strip()
        sintomas = self.entry_sintomas.get().strip()

        # 1. Validação de campos obrigatórios
        if not nome or len(nome) < 3:
            messagebox.showwarning("Campo Obrigatório", "Por favor, informe o nome completo do paciente (mínimo 3 caracteres).")
            self.entry_nome.focus_set()
            return

        cpf_digitos = "".join(filter(str.isdigit, cpf_raw))
        if len(cpf_digitos) != 11:
            messagebox.showwarning("CPF Inválido", "O CPF deve conter exatamente 11 dígitos numéricos.")
            self.entry_cpf.focus_set()
            return

        if not idade_str.isdigit() or not (0 <= int(idade_str) <= 125):
            messagebox.showwarning("Idade Inválida", "Informe uma idade válida entre 0 e 125 anos.")
            self.entry_idade.focus_set()
            return

        if not sintomas or len(sintomas) < 3:
            messagebox.showwarning("Sintomas Obrigatórios", "Descreva a queixa principal ou sintomas apresentados pelo paciente.")
            self.entry_sintomas.focus_set()
            return

        # Higienização de caracteres que violam o protocolo IPC CSV delimitado por ';'
        nome_limpo = nome.replace(";", " ").replace("\n", " ").strip()
        sintomas_limpos = sintomas.replace(";", ",").replace("\n", " ").strip()
        idade = int(idade_str)

        # 2. Invocação síncrona do Daemon C via Conexão IPC
        try:
            resultado = self.backend.inserir_paciente(
                cpf=cpf_digitos,
                nome=nome_limpo,
                idade=idade,
                sintomas=sintomas_limpos,
                classificacao=self.cor_selecionada,
                prioridade=self.prioridade_selecionada
            )

            if resultado.get("sucesso"):
                novo_id = resultado["id_prontuario"]
                tamanho_heap = resultado.get("tamanho_heap", 0)

                # Estrutura dados do paciente recém-cadastrado
                paciente = {
                    "id_prontuario": novo_id,
                    "cpf": cpf_digitos,
                    "nome": nome_limpo,
                    "idade": idade,
                    "sintomas": sintomas_limpos,
                    "classificacao": self.cor_selecionada,
                    "prioridade": self.prioridade_selecionada,
                    "horario_chegada": int(time.time()),
                    "status": "Aguardando",
                    "tamanho_heap": tamanho_heap
                }

                self.paciente_recem_inserido = paciente
                self.historico_sessao.insert(0, paciente)

                # Atualiza componentes visuais locais
                self._renderizar_confirmacao_sucesso()
                self._atualizar_historico_sessao()
                self._limpar_formulario()

                # Dispara sincronizacao reativa com a janela principal e outras abas
                if self.callback_atualizar_sistema:
                    self.callback_atualizar_sistema()

                messagebox.showinfo(
                    "Triagem Concluída com Sucesso",
                    f"Paciente: {nome_limpo}\n"
                    f"Prontuário Nº: {novo_id}\n"
                    f"Classificação: {self.cor_selecionada} (Prioridade {self.prioridade_selecionada})\n"
                    f"Posição no Max-Heap: ~{tamanho_heap} na fila\n\n"
                    "O paciente já está disponível no índice da AVL e pronto para ser chamado no Consultório!"
                )
            else:
                msg_erro = resultado.get("mensagem", "Erro desconhecido retornado pelo backend.")
                messagebox.showerror("Erro na Inserção", f"Não foi possível cadastrar o paciente:\n\n{msg_erro}")

        except Exception as e:
            messagebox.showerror("Falha Crítica", f"Ocorreu um erro durante a comunicação com o backend C:\n\n{e}")
