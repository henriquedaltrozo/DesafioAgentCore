
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from reclamacoes_analyzer import ReclamacoesAnalyzer
import os
import json
from datetime import datetime
import numpy as np
import pandas as pd

def make_json_serializable(obj):
    """Converte objetos para tipos serializáveis em JSON"""
    if isinstance(obj, dict):
        return {str(k): make_json_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [make_json_serializable(v) for v in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, pd.DataFrame):
        return obj.to_dict('records')
    elif isinstance(obj, pd.Series):
        return obj.to_dict()
    else:
        return obj

app = BedrockAgentCoreApp()
agent = Agent()

@app.entrypoint
def invoke(payload):
    """AI agent para análise de reclamações e geração de relatórios"""
    user_message = payload.get("prompt", "Gerar relatório de reclamações")
    
    try:
        # Caminho para o arquivo JSON
        json_file_path = "reclamacoes_20251001_220605.json"
        
        # Verificar se o arquivo existe
        if not os.path.exists(json_file_path):
            return {
                "result": "Erro: Arquivo de reclamações não encontrado.",
                "status": "error"
            }
        
        # Criar instância do analisador
        analyzer = ReclamacoesAnalyzer(json_file_path)
        
        # Carregar os dados
        if not analyzer.load_data():
            return {
                "result": "Erro ao carregar os dados do arquivo JSON.",
                "status": "error"
            }
        
        # Gerar resumo textual
        summary = analyzer.generate_summary_text()
        
        # Gerar relatório em PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"relatorio_reclamacoes_{timestamp}.pdf"
        
        pdf_success = analyzer.generate_pdf_report(pdf_filename)
        
        # Obter estatísticas detalhadas
        categoria_analysis = analyzer.analyze_categories()
        status_analysis = analyzer.analyze_status()
        trends = analyzer.analyze_trends()
        
        # Converter trends para formato JSON serializável
        trends_serializable = {
            'date_range': trends['date_range'],
            'daily_trends_count': len(trends['daily_trends']) if hasattr(trends['daily_trends'], '__len__') else 0,
            'weekly_trends_summary': {str(k): int(v) for k, v in trends['weekly_trends'].items()} if hasattr(trends['weekly_trends'], 'items') else {}
        }
        
        result = {
            "summary": summary,
            "categoria_analysis": make_json_serializable(categoria_analysis),
            "status_analysis": make_json_serializable(status_analysis),
            "trends": trends_serializable,
            "pdf_generated": pdf_success,
            "pdf_filename": pdf_filename if pdf_success else None,
            "status": "success"
        }
        
        # Usar o agente para gerar insights adicionais
        agent_prompt = f"""
        Com base nos dados de reclamações analisados, forneça insights estratégicos:
        
        Resumo dos dados:
        {summary}
        
        Categorias: {categoria_analysis}
        Status: {status_analysis}
        
        Por favor, forneça recomendações para:
        1. Melhorar o atendimento ao cliente
        2. Reduzir as reclamações mais frequentes
        3. Priorizar ações corretivas
        """
        
        agent_result = agent(agent_prompt)
        result["ai_insights"] = agent_result.message
        
        return result
        
    except Exception as e:
        return {
            "result": f"Erro durante a análise: {str(e)}",
            "status": "error"
        }

def executar_analise_rapida():
    """Execução rápida e limpa do sistema de análise"""
    print("🏦 SISTEMA DE ANÁLISE DE RECLAMAÇÕES - SICREDI")
    print("=" * 60)
    
    # Verificar se o arquivo de dados existe
    data_file = "reclamacoes_20251001_220605.json"
    if not os.path.exists(data_file):
        print(f"❌ Arquivo {data_file} não encontrado!")
        return
    
    print("🔄 Executando análise completa...")
    
    try:
        result = invoke({"prompt": "Analisar reclamações e gerar relatório"})
        
        if result.get("status") == "success":
            print("✅ Análise concluída com sucesso!")
            print("\n📊 RESULTADOS:")
            print(f"   • Total de categorias analisadas: {len(result['categoria_analysis'])}")
            print(f"   • Total de status analisados: {len(result['status_analysis'])}")
            print(f"   • PDF gerado: {result['pdf_filename']}")
            print(f"   • Período analisado: {result['trends']['date_range']['start']} a {result['trends']['date_range']['end']}")
            
            # Mostrar insights principais
            print("\n💡 CATEGORIAS MAIS PROBLEMÁTICAS:")
            for categoria, dados in sorted(result['categoria_analysis'].items(), 
                                         key=lambda x: x[1]['count'], reverse=True)[:3]:
                print(f"   • {categoria}: {dados['count']} reclamações ({dados['percentage']}%)")
            
            print("\n📈 STATUS DAS RECLAMAÇÕES:")
            for status, dados in result['status_analysis'].items():
                print(f"   • {status}: {dados['count']} ({dados['percentage']}%)")
            
            # Calcular métricas importantes
            resolvidos = result['status_analysis'].get('Resolvido', {}).get('count', 0)
            total = sum(dados['count'] for dados in result['status_analysis'].values())
            taxa_resolucao = (resolvidos / total) * 100
            print(f"\n📊 TAXA DE RESOLUÇÃO: {taxa_resolucao:.1f}%")
            
            if taxa_resolucao < 50:
                print("🚨 CRÍTICO: Taxa de resolução muito baixa!")
            elif taxa_resolucao < 70:
                print("⚠️  ATENÇÃO: Taxa de resolução abaixo do ideal")
            else:
                print("✅ Taxa de resolução dentro do esperado")
            
        else:
            print(f"❌ Erro na análise: {result.get('result', 'Erro desconhecido')}")
            
    except Exception as e:
        print(f"❌ Erro durante a execução: {e}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    # Execução rápida como padrão
    executar_analise_rapida()
    
    # Iniciar o app Bedrock (comentado para execução rápida)
    # app.run()
        