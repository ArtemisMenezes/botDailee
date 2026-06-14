import os
import json
from google import genai
from collections import Counter
from dotenv import load_dotenv

# Configuração da IA
load_dotenv(override=True)
API_KEY = os.getenv('API_KEY')
client = genai.Client(api_key=API_KEY)

# Função de calcular a porcentagem por etiqueta de cada aluno
def calc_percentage(anotacoes):
    """Calcula as porcentagens de cada etiqueta nas anotações de um aluno """
    etiquetas = []
    for nota in anotacoes:
        etiquetas.extend(nota["etiquetas"])
        
    if not etiquetas:
        return {}

    total_etiquetas = len(etiquetas)
    contagem_etiquetas = Counter(etiquetas)

    porcentagens = {}
    for etiqueta, quantidade in contagem_etiquetas.items():
        porcentagens[etiqueta] = round((quantidade / total_etiquetas) * 100, 1)

    # retornando listagem ordenado do maior para o menor
    return dict(sorted(porcentagens.items(), key=lambda item: item[1], reverse=True))

# Função de gerar o resumo utilizando inteligência artificial
def gen_resumo(nome_aluno, anotacoes):
    """Usando o Gemini para ler as descrições e gerar um resumo"""
    todas_descricoes = "\n".join([nota["descricao"] for nota in anotacoes])

    prompt = f"""
    Você é um Assistente especialista em educação especial(AEE). 
    Abaixo estão as anotaçoes diárias do mês do aluno {nome_aluno}.
    Escreva um resumo de um parágrafo sobre o desenvolvimento do aluno neste mês,
    destacando os pontos que ele evoluiu e principais desafios enfrentados.
    Seja empático e profissional.

    Anotações: {todas_descricoes}
    """

    resposta = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    return resposta.text

# Função para gerar o relatório completo
def gen_relatorio(nome_aluno, database):
    """Função principal que vai chamar quando o usuário selecionar um aluno"""
    
    # Procurando um aluno no JSON
    aluno_encontrado = None
    for aluno in database["alunos"]:
        if aluno["nome"].lower() == nome_aluno.lower():
            aluno_encontrado = aluno
            break
            
    # Retorna erro se não encontrar o aluno
    if not aluno_encontrado:
        return f"Erro: O aluno '{nome_aluno}' não foi encontrado no sistema"
    
    # Se encontrou puxa as anotações
    anotacoes = aluno_encontrado["anotacoes"]

    # Calculando as porcentagens
    estatisticas = calc_percentage(anotacoes)

    # Pede pra IA gerar o resumo
    resumo = gen_resumo(aluno_encontrado["nome"], anotacoes)

    # Monta o relatorio final
    relatorio = f"RELATÓRIO MENSAL: {aluno_encontrado['nome'].upper()}\n\n"
    relatorio += "Visão Geral:\n"
    for etiqueta, perc in estatisticas.items():
        relatorio += f"- {etiqueta.capitalize()}: {perc}%\n"
    
    relatorio += f"\n Resumo Geral do Mês (Gerado por IA):\n{resumo}\n"

    return relatorio

try:
    with open('data.json', 'r', encoding='utf-8') as arquivo:
        banco_de_dados_python = json.load(arquivo)
        
    # Testando um aluno
    aluno_clicado = "João Guilherme" 

    # Imprimindo no terminal
    print(gen_relatorio(aluno_clicado, banco_de_dados_python))

except FileNotFoundError:
    print("Erro: O arquivo 'data.json' não foi encontrado.")
except json.JSONDecodeError:
    print("Erro: O arquivo 'data.json' está com a formatação inválida.")