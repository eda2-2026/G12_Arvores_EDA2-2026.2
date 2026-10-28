import os
import csv
import random
from datetime import datetime

random.seed(42)

NOMES_MASCULINOS = [
    "Lucas", "Gabriel", "Matheus", "Pedro", "Guilherme", "Gustavo", "Felipe", "Rafael", "Leonardo", "Enzo",
    "Arthur", "Bernardo", "Heitor", "Davi", "Lorenzo", "Theo", "Isaac", "Samuel", "Miguel", "Joao",
    "Henrique", "Caua", "Vitor", "Eduardo", "Alexandre", "Rodrigo", "Bruno", "Thiago", "Diego", "Andre",
    "Marcelo", "Fernando", "Ricardo", "Daniel", "Carlos", "Marcos", "Antonio", "Jose", "Francisco", "Paulo",
    "Luiz", "Otavio", "Murilo", "Vinicius", "Caio", "Igor", "Renan", "Renato", "Augusto", "Breno"
]

NOMES_FEMININOS = [
    "Alice", "Sophia", "Helena", "Valentina", "Laura", "Isabella", "Manuela", "Julia", "Heloisa", "Luiza",
    "Maria", "Lorena", "Livia", "Giovanna", "Beatriz", "Mariana", "Cecilia", "Lara", "Emanuelly", "Yasmin",
    "Melissa", "Isadora", "Ana", "Clara", "Marina", "Carolina", "Camila", "Larissa", "Amanda", "Leticia",
    "Bianca", "Gabriela", "Bruna", "Fernanda", "Jessica", "Aline", "Vanessa", "Patricia", "Juliana", "Renata",
    "Tatiane", "Daniela", "Flavia", "Priscila", "Debora", "Rebeca", "Raquel", "Sarah", "Nicole", "Agatha"
]

SOBRENOMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves", "Pereira", "Lima", "Gomes",
    "Costa", "Ribeiro", "Martins", "Carvalho", "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
    "Rocha", "Dias", "Nascimento", "Andrade", "Moreira", "Nunes", "Marques", "Machado", "Mendes", "Freitas",
    "Cardoso", "Ramos", "Goncalves", "Santana", "Teixeira", "Pinto", "Cavalcanti", "Castro", "Campos", "Monteiro",
    "Moraes", "Neves", "Pacheco", "Barros", "Rezende", "Guimaraes", "Borges", "Siqueira", "Dantas", "Batista",
    "Tavares", "Vasconcelos", "Meireles", "Sales", "Viana", "Assis", "Aguiar", "Macedo", "Cunha", "Farias",
    "Peixoto", "Brandao", "Figueiredo", "Fonseca", "Antunes", "Paiva", "Bezerra", "Sampaio", "Menezes", "Brito",
    "Carneiro", "Pimentel", "Xavier", "Valente", "Pinheiro"
]

def gerar_nome_completo(sexo):

    if sexo == "F":
        primeiro = random.choice(NOMES_FEMININOS)
    elif sexo == "M":
        primeiro = random.choice(NOMES_MASCULINOS)
    else:
        primeiro = random.choice(NOMES_MASCULINOS + NOMES_FEMININOS)

    if random.random() < 0.5:
        sobrenome = random.choice(SOBRENOMES)
        return f"{primeiro} {sobrenome}"
    else:
        s1, s2 = random.sample(SOBRENOMES, 2)
        return f"{primeiro} {s1} {s2}"

def gerar_cpf_valido(seq):

    base = [int(d) for d in f"{seq:09d}"]
    soma1 = sum(base[i] * (10 - i) for i in range(9))
    d1 = (soma1 * 10) % 11
    if d1 >= 10:
        d1 = 0
    soma2 = sum(base[i] * (11 - i) for i in range(9)) + (d1 * 2)
    d2 = (soma2 * 10) % 11
    if d2 >= 10:
        d2 = 0
    return "".join(map(str, base)) + f"{d1}{d2}"

def extrair_sintomas(row):
    sintomas = []
    if row.get("SATURACAO") == "1":
        sintomas.append("Queda saturacao O2 (<95%)")
    if row.get("DISPNEIA") == "1":
        sintomas.append("Falta de ar aguda")
    if row.get("DESC_RESP") == "1":
        sintomas.append("Desconforto respiratorio")
    if row.get("FEBRE") == "1":
        sintomas.append("Febre alta")
    if row.get("TOSSE") == "1":
        sintomas.append("Tosse persistente")
    if row.get("GARGANTA") == "1":
        sintomas.append("Dor de garganta")
    if row.get("VOMITO") == "1" or row.get("DIARREIA") == "1":
        sintomas.append("Sintomas gastrointestinais")
    
    if not sintomas:
        sintomas.append("Quadro clinico geral estavel")

    texto = ", ".join(sintomas)
    if len(texto) > 120:
        texto = texto[:120].rsplit(", ", 1)[0]
    return texto.strip()

def classificar_manchester(row):
    uti = row.get("UTI", "") == "1"
    sup_inv = row.get("SUPORT_VEN", "") == "1"
    sup_nao = row.get("SUPORT_VEN", "") == "2"
    sat = row.get("SATURACAO", "") == "1"
    desc = row.get("DESC_RESP", "") == "1"
    disp = row.get("DISPNEIA", "") == "1"
    febre = row.get("FEBRE", "") == "1"
    tosse = row.get("TOSSE", "") == "1"
    garg = row.get("GARGANTA", "") == "1"
    vom = row.get("VOMITO", "") == "1"
    diar = row.get("DIARREIA", "") == "1"

    score = 0
    if uti and sup_inv:
        score += 6
    elif uti:
        score += 4
    elif sup_nao:
        score += 3

    if sat and desc:
        score += 3
    elif sat or desc:
        score += 2

    if disp:
        score += 2
    if febre:
        score += 1
    if tosse:
        score += 1
    if garg:
        score += 1
    if diar or vom:
        score += 1

    if score >= 13:
        return 5, "Vermelho"
    elif score >= 11:
        return 4, "Laranja"
    elif score >= 8:
        return 3, "Amarelo"
    elif score >= 5:
        return 2, "Verde"
    else:
        return 1, "Azul"

def converter_timestamp(dt_str, indice):

    try:
        dt_limpa = dt_str.split("T")[0]
        dt = datetime.strptime(dt_limpa, "%Y-%m-%d")
        ts = int(dt.timestamp())
        ts += (indice * 17) % 86400
        return ts
    except Exception:
        # Fallback para timestamp base de 2019
        return 1563753600 + (indice * 17) % 86400

def main():
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    raiz_projeto = os.path.abspath(os.path.join(diretorio_atual, ".."))
    caminho_entrada = os.path.join(raiz_projeto, "INFLUD19-23-03-2026.csv")

    if not os.path.exists(caminho_entrada):
        caminho_entrada = os.path.join(raiz_projeto, "dados", "INFLUD19-23-03-2026.csv")

    if not os.path.exists(caminho_entrada):
        print(f"Erro: Arquivo bruto nao encontrado em {caminho_entrada}")
        return

    pasta_dados = os.path.join(raiz_projeto, "dados")
    os.makedirs(pasta_dados, exist_ok=True)
    caminho_saida = os.path.join(pasta_dados, "pacientes.csv")

    print(f"Lendo base bruta do SUS: {caminho_entrada} ...")
    
    total_processados = 0
    cpfs_gerados = set()
    contagem_manchester = {"Vermelho": 0, "Laranja": 0, "Amarelo": 0, "Verde": 0, "Azul": 0}

    with open(caminho_entrada, mode="r", encoding="utf-8", errors="ignore") as f_in, \
         open(caminho_saida, mode="w", encoding="utf-8", newline="") as f_out:
        
        leitor = csv.DictReader(f_in, delimiter=";")
        escritor = csv.writer(f_out, delimiter=";")

        escritor.writerow([
            "id_prontuario", "cpf", "nome", "idade", 
            "sintomas", "classificacao", "prioridade", 
            "horario_chegada", "status"
        ])

        for i, row in enumerate(leitor, start=1):
            id_prontuario = i

            cpf = gerar_cpf_valido(i)
            cpfs_gerados.add(cpf)

            sexo = row.get("CS_SEXO", "").strip().upper()
            nome = gerar_nome_completo(sexo)

            idade_str = row.get("NU_IDADE_N", "0").strip()
            try:
                idade = int(float(idade_str))
                if idade < 0 or idade > 120:
                    idade = 30
            except ValueError:
                idade = 30

            sintomas = extrair_sintomas(row)

            prioridade, classificacao = classificar_manchester(row)
            contagem_manchester[classificacao] += 1

            dt_str = row.get("DT_NOTIFIC", "")
            horario_chegada = converter_timestamp(dt_str, i)

            status = "Aguardando"

            escritor.writerow([
                id_prontuario, cpf, nome, idade, 
                sintomas, classificacao, prioridade, 
                horario_chegada, status
            ])
            total_processados += 1

    print("\nProcessamento concluido com sucesso!")
    print(f"Total de pacientes gerados: {total_processados}")
    print(f"Total de CPFs unicos: {len(cpfs_gerados)}")
    print("\nDistribuicao do Protocolo de Manchester (Fila do Heap):")
    for cor, qtd in contagem_manchester.items():
        pct = (qtd / total_processados) * 100
        print(f"  {cor:10}: {qtd:5d} ({pct:5.1f}%)")
    print(f"\nArquivo gerado em: {caminho_saida}")

if __name__ == "__main__":
    main()
