"""
Modulo de configuracoes visuais e paleta oficial do Protocolo de Manchester.
Fornece cores, badges e formatadores para a interface grafica.
"""

from datetime import datetime

# Paleta oficial com alto contraste para o tema escuro
CORES_MANCHESTER = {
    "Vermelho": {
        "fundo": "#D32F2F",
        "texto": "#FFFFFF",
        "fundo_suave": "#3A1B1B",
        "borda": "#EF5350",
        "rotulo": "🔴 Vermelho - Emergencia (Prioridade 5)"
    },
    "Laranja": {
        "fundo": "#F57C00",
        "texto": "#FFFFFF",
        "fundo_suave": "#3A291B",
        "borda": "#FFA726",
        "rotulo": "🟠 Laranja - Muito Urgente (Prioridade 4)"
    },
    "Amarelo": {
        "fundo": "#FBC02D",
        "texto": "#212121",
        "fundo_suave": "#3A351B",
        "borda": "#FFEE58",
        "rotulo": "🟡 Amarelo - Urgente (Prioridade 3)"
    },
    "Verde": {
        "fundo": "#388E3C",
        "texto": "#FFFFFF",
        "fundo_suave": "#1B3A1E",
        "borda": "#66BB6A",
        "rotulo": "🟢 Verde - Pouco Urgente (Prioridade 2)"
    },
    "Azul": {
        "fundo": "#1976D2",
        "texto": "#FFFFFF",
        "fundo_suave": "#1B2A3A",
        "borda": "#42A5F5",
        "rotulo": "🔵 Azul - Nao Urgente (Prioridade 1)"
    }
}

COR_PADRAO = {
    "fundo": "#424242",
    "texto": "#FFFFFF",
    "fundo_suave": "#2B2B2B",
    "borda": "#616161",
    "rotulo": "⚪ Sem Classificacao"
}

def obter_estilo_manchester(classificacao: str) -> dict:
    """Retorna o dicionario de estilo para a classificacao informada."""
    if not classificacao:
        return COR_PADRAO
    return CORES_MANCHESTER.get(str(classificacao).strip().capitalize(), COR_PADRAO)

def formatar_cpf(cpf: str) -> str:
    """Formata um CPF de 11 digitos numericos para o formato 000.000.000-00."""
    if not cpf:
        return "---"
    limpo = "".join(filter(str.isdigit, str(cpf)))
    if len(limpo) == 11:
        return f"{limpo[:3]}.{limpo[3:6]}.{limpo[6:9]}-{limpo[9:]}"
    return cpf

def formatar_timestamp(timestamp: int) -> str:
    """Converte um timestamp Unix em data e hora legivel (DD/MM/AAAA HH:MM)."""
    try:
        dt = datetime.fromtimestamp(int(timestamp))
        return dt.strftime("%d/%m/%Y %H:%M")
    except Exception:
        return "Horario Indisponivel"
