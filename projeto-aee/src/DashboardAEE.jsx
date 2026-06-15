import React, { useState, useEffect } from 'react';

export default function DashboardAEE() {
  const [alunoSelecionado, setAlunoSelecionado] = useState("Pedro Rafael");
  const [dadosDoAluno, setDadosDoAluno] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState(null);

  // Lista de alunos para o menu
  const listaAlunos = ["Pedro Rafael", "Maria Estela", "João Guilherme"];

  // Efeito de carregando que vai rodar sempre que buscar um novo aluno
  useEffect(() => {
    async function buscarDadosNoPython() {
      setCarregando(true);
      setErro(null);
      
      try {
        // Chamando API Flask
        const resposta = await fetch(`http://localhost:5000/api/relatorio/${alunoSelecionado}`);
        const dados = await resposta.json();

        if (!resposta.ok) {
          throw new Error(dados.erro || "Erro ao buscar dados");
        }

        setDadosDoAluno(dados);
      } catch (error) {
        setErro(error.message);
      } finally {
        setCarregando(false);
      }
    }

    buscarDadosNoPython();
  }, [alunoSelecionado]);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-12 font-sans">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Filtro */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-slate-900">Painel de Acompanhamento AEE</h1>
          </div>
          <select 
            value={alunoSelecionado}
            onChange={(e) => setAlunoSelecionado(e.target.value)}
            className="w-full sm:w-64 px-4 py-2.5 rounded-xl border border-slate-200 bg-slate-50 text-slate-700"
          >
            {listaAlunos.map(nome => (
              <option key={nome} value={nome}>{nome}</option>
            ))}
          </select>
        </div>

        {/* Estados de Carregamento e Erro */}
        {carregando && <p className="text-center text-indigo-600 font-medium animate-pulse">Consultando a IA do Gemini para gerar o resumo...</p>}
        {erro && <p className="text-center text-red-500 bg-red-50 p-4 rounded-xl border border-red-200">{erro}</p>}

        {/* Exibindo os Dados do python */}
        {!carregando && dadosDoAluno && !erro && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            
            {/* Card de Frequência */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100">
              <h2 className="text-lg font-bold mb-4">Análise de Frequência</h2>
              <div className="space-y-4">
                {Object.entries(dadosDoAluno.estatisticas).map(([etiqueta, perc]) => (
                  <div key={etiqueta}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="capitalize font-medium text-slate-600">{etiqueta}</span>
                      <span className="font-bold text-slate-800">{perc}%</span>
                    </div>
                    <div className="w-full bg-slate-100 rounded-full h-3">
                      <div 
                        className="bg-indigo-500 h-full rounded-full transition-all duration-1000" 
                        style={{ width: `${perc}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Card de Resumo da IA */}
            <div className="bg-white rounded-2xl p-6 shadow-sm border border-slate-100 border-l-4 border-l-indigo-500">
              <h2 className="text-lg font-bold mb-4 flex items-center gap-2">Resumo da IA</h2>
              <p className="text-slate-700 text-sm leading-relaxed whitespace-pre-wrap">
                {dadosDoAluno.resumo}
              </p>
            </div>

          </div>
        )}
      </div>
    </div>
  );
}

