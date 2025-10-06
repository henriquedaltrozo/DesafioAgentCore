#!/usr/bin/env python3
"""
🚀 Servidor Bedrock AgentCore - Agente de IA
Executa o agente como serviço de IA conversacional
"""

from my_agent import app
import os
from dotenv import load_dotenv

# Carregar configurações
load_dotenv()

def start_ai_agent():
    """Inicia o agente de IA como serviço Bedrock"""
    
    print("🤖 INICIANDO AGENTE DE IA - BEDROCK AGENTCORE")
    print("=" * 55)
    print("🔧 Configurações:")
    print(f"   • Região AWS: us-east-1")
    print(f"   • Modelo IA: Claude 3 Sonnet")
    print(f"   • Dados: reclamacoes_20251001_220605.json")
    print(f"   • Modo: Conversacional + Análise")
    print("=" * 55)
    
    # Verificar arquivo de dados
    if not os.path.exists("reclamacoes_20251001_220605.json"):
        print("⚠️  AVISO: Arquivo de dados não encontrado!")
        print("   O agente funcionará apenas em modo conversacional básico")
    else:
        print("✅ Dados de reclamações carregados")
    
    print("\n🚀 Iniciando servidor Bedrock...")
    print("📡 O agente estará disponível via:")
    print("   • API REST (HTTP)")
    print("   • Bedrock Agent Runtime")
    print("   • Integração com aplicações")
    
    print("\n💡 Exemplos de uso:")
    print("   • 'Qual a situação das reclamações?'")
    print("   • 'Como melhorar o atendimento?'")
    print("   • 'Analisar reclamações e gerar relatório'")
    print("   • 'Enviar relatório para email@exemplo.com'")
    
    print("\n🔄 Pressione Ctrl+C para parar o servidor")
    print("-" * 55)
    
    try:
        # Iniciar o app Bedrock
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro no servidor: {e}")

if __name__ == "__main__":
    start_ai_agent()