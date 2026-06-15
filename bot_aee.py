import os
import json
from flask import Flask, jsonify
from flask_cors import CORS
from google import genai
from collections import Counter
from dotenv import load_dotenv

# Inicializando o Flask
app = Flask(__name__)
CORS(app) 

# Configuração da IA
load_dotenv(override=True)
API_KEY = os.getenv('API_KEY')
client = genai.Client(api_key=API_KEY)

#  Função de calcular a porcentagem 
def calc_percentage(anotacoes):
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

    return dict(sorted(porcentagens.items(), key=lambda item: item[1], reverse=True))

#  Função de gerar o resumo (mantida igual a sua)
def gen_resumo(nome_aluno, anotacoes):
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

#  Rota da API que o React vai chamar
@app.route('/api/relatorio/<nome_aluno>', methods=['GET'])
def gerar_relatorio_api(nome_aluno):
    try:
        with open('data.json', 'r', encoding='utf-8') as arquivo:
            database = json.load(arquivo)
            
        # Procurando o aluno
        aluno_encontrado = None
        for aluno in database["alunos"]:
            if aluno["nome"].lower() == nome_aluno.lower():
                aluno_encontrado = aluno
                break
                
        if not aluno_encontrado:
            return jsonify({"erro": f"O aluno '{nome_aluno}' não foi encontrado"}), 404
            
        anotacoes = aluno_encontrado["anotacoes"]
        
        # Gerando os dados
        estatisticas = calc_percentage(anotacoes)
        resumo_ia = gen_resumo(aluno_encontrado["nome"], anotacoes)

        # Em vez de retornar um texto puro, retornamos um JSON!
        return jsonify({
            "nome": aluno_encontrado["nome"],
            "estatisticas": estatisticas,
            "resumo": resumo_ia,
            "total_anotacoes": len(anotacoes)
        }), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Rodando o servidor
if __name__ == '__main__':
    print("Servidor Flask rodando na porta 5000...")
    app.run(debug=True, port=5000)